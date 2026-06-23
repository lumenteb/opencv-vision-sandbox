import cv2
import numpy as np
import time


def get_red_mask(frame):
    """
    Creates a cleaner mask for red color using HSV color space.
    Includes blur + morphology to reduce noise.
    """
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)

    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    lower_red_1 = np.array([0, 120, 70])
    upper_red_1 = np.array([10, 255, 255])

    lower_red_2 = np.array([170, 120, 70])
    upper_red_2 = np.array([180, 255, 255])

    mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    mask = mask_1 + mask_2

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def find_largest_contour(mask, min_area=500):
    """
    шукаємо найбільший контур
    """
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)

    if area < min_area:
        return None

    return largest_contour


def get_object_data(contour):
    """
   робимо рамочку та шукаємо центр
    """
    x, y, w, h = cv2.boundingRect(contour)

    center_x = x + w // 2
    center_y = y + h // 2

    return x, y, w, h, center_x, center_y


def get_direction(center_x, center_y, previous_x, previous_y):
    """
   шукаємо рух відносно зміни кадрів
    """
    direction = ""

    if previous_x is not None and previous_y is not None:
        dx = center_x - previous_x
        dy = center_y - previous_y

        if abs(dx) > abs(dy):
            if dx > 10:
                direction = "MOVING RIGHT"
            elif dx < -10:
                direction = "MOVING LEFT"
        else:
            if dy > 10:
                direction = "MOVING DOWN"
            elif dy < -10:
                direction = "MOVING UP"

    return direction


def get_control_text(error_x, frame_width):
    """
    командир для центрування
    """
    max_error = frame_width // 2
    control_power = int(abs(error_x) / max_error * 100)

    if abs(error_x) < 30:
        return "TARGET LOCKED"
    elif error_x < 0:
        return f"TURN LEFT: {control_power}%"
    else:
        return f"TURN RIGHT: {control_power}%"


def calculate_speed(center_x, center_y, previous_center_x, previous_center_y):
    """
   швидкість
    """
    if previous_center_x is None or previous_center_y is None:
        return 0, 0, 0

    speed_x = center_x - previous_center_x
    speed_y = center_y - previous_center_y
    total_speed = int((speed_x ** 2 + speed_y ** 2) ** 0.5)

    return speed_x, speed_y, total_speed


def predict_position(center_x, center_y, speed_x, speed_y, frame_width, frame_height):
    """
   передбачення положеня
    """
    prediction_frames = 5

    predicted_x = center_x + speed_x * prediction_frames
    predicted_y = center_y + speed_y * prediction_frames

    predicted_x = max(0, min(frame_width, predicted_x))
    predicted_y = max(0, min(frame_height, predicted_y))

    return int(predicted_x), int(predicted_y)


def draw_trajectory(frame, points):
    """
    лінія переміщення по ходу
    """
    for i in range(1, len(points)):
        cv2.line(
            frame,
            points[i - 1],
            points[i],
            (255, 255, 0),
            2
        )


def draw_screen_guides(frame, frame_width, frame_height):
    """
  ліво право та центр
    """
    left_border = frame_width // 3
    right_border = frame_width * 2 // 3
    screen_center_x = frame_width // 2

    # лывоборт
    cv2.line(
        frame,
        (left_border, 0),
        (left_border, frame_height),
        (255, 255, 255),
        2
    )

    # правоборт
    cv2.line(
        frame,
        (right_border, 0),
        (right_border, frame_height),
        (255, 255, 255),
        2
    )

    # центр екрана
    cv2.line(
        frame,
        (screen_center_x, 0),
        (screen_center_x, frame_height),
        (0, 0, 255),
        2
    )

def draw_debug_panel(frame, object_status, current_area, fps, system_state):
    """
    дебажка

    """
    panel_x = 30
    panel_y = 210
    line_height = 30

    cv2.putText(
        frame,
        f"STATE: {system_state}",
        (panel_x, panel_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"OBJECT: {object_status}",
        (panel_x, panel_y + line_height),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"AREA: {current_area}",
        (panel_x, panel_y + line_height * 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"FPS: {fps}",
        (panel_x, panel_y + line_height * 3),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

STATE_SEARCHING = "SEARCHING"
STATE_TRACKING = "TRACKING"
STATE_HOLDING = "HOLDING"
STATE_LOST = "LOST"


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera not found")
        return

    previous_x = None
    previous_y = None

    previous_center_x = None
    previous_center_y = None

    points = []

    previous_time = time.time()
    fps = 0
    object_status = "NOT DETECTED"
    current_area = 0

    last_known_position = None
    frames_without_detection = 0
    max_lost_frames = 10

    system_state = STATE_SEARCHING

    aim_x = None
    aim_y = None
    gimbal_gain = 0.2

    while True:
        success, frame = camera.read()

        if not success:
            print("Failed to read frame")
            break

        current_time = time.time()
        delta_time = current_time - previous_time

        if delta_time > 0:
            fps = int(1 / delta_time)

        previous_time = current_time


        frame_height, frame_width = frame.shape[:2]
        screen_center_x = frame_width // 2

        if aim_x is None or aim_y is None:
            aim_x = frame_width // 2
            aim_y = frame_height // 2

        mask = get_red_mask(frame)
        contour = find_largest_contour(mask)

        object_status = "NOT DETECTED"
        current_area = 0

        if contour is not None:
            object_status = "DETECTED"
            current_area = int(cv2.contourArea(contour))
            system_state = STATE_TRACKING

            x, y, w, h, center_x, center_y = get_object_data(contour)

            aim_error_x = center_x - aim_x
            aim_error_y = center_y - aim_y

            aim_x = aim_x + aim_error_x * gimbal_gain
            aim_y = aim_y + aim_error_y * gimbal_gain

            last_known_position = (center_x, center_y)
            frames_without_detection = 0
           
            direction = get_direction(
                center_x,
                center_y,
                previous_x,
                previous_y
            )

            previous_x = center_x
            previous_y = center_y

           
            points.append((center_x, center_y))

            if len(points) > 30:
                points.pop(0)

           
            error_x = center_x - screen_center_x

           
            control_text = get_control_text(error_x, frame_width)

          
            speed_x, speed_y, total_speed = calculate_speed(
                center_x,
                center_y,
                previous_center_x,
                previous_center_y
            )

            previous_center_x = center_x
            previous_center_y = center_y

          
            predicted_x, predicted_y = predict_position(
                center_x,
                center_y,
                speed_x,
                speed_y,
                frame_width,
                frame_height
            )

           
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            
            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (255, 0, 0),
                -1
            )

            
            cv2.circle(
                frame,
                (predicted_x, predicted_y),
                8,
                (0, 0, 255),
                -1
            )

           
            cv2.line(
                frame,
                (center_x, center_y),
                (predicted_x, predicted_y),
                (0, 0, 255),
                2
            )

            
            cv2.putText(
                frame,
                f"X:{center_x} Y:{center_y}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

 
            cv2.putText(
                frame,
                direction,
                (x, y + h + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"ERROR X: {error_x}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                control_text,
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                3
            )

            cv2.putText(
                frame,
                f"SPEED: {total_speed} px/frame",
                (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

           
            cv2.putText(
                frame,
                f"PREDICTED: X:{predicted_x} Y:{predicted_y}",
                (30, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        else:
            frames_without_detection += 1

            if last_known_position is None:
                system_state = STATE_SEARCHING
                object_status = "SEARCHING"

            elif frames_without_detection <= max_lost_frames:
                system_state = STATE_HOLDING
                object_status = "HOLDING LAST POSITION"

                last_x, last_y = last_known_position

                cv2.circle(
                    frame,
                    (last_x, last_y),
                    10,
                    (0, 165, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "HOLDING LAST POSITION",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 165, 255),
                    3
                )

            else:
                system_state = STATE_LOST
                object_status = "LOST TARGET"
                last_known_position = None
                points.clear()

        # треактори
        draw_trajectory(frame, points)

        # зони лини
        draw_screen_guides(frame, frame_width, frame_height)

        draw_debug_panel(frame, object_status, current_area, fps, system_state)

        aim_x_int = int(aim_x)
        aim_y_int = int(aim_y)

        cv2.circle(
            frame,
            (aim_x_int, aim_y_int),
            18,
            (255, 0, 255),
            2
        )

        cv2.line(
            frame,
            (aim_x_int - 25, aim_y_int),
            (aim_x_int + 25, aim_y_int),
            (255, 0, 255),
            2
        )

        cv2.line(
            frame,
            (aim_x_int, aim_y_int - 25),
            (aim_x_int, aim_y_int + 25),
            (255, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"AIM X:{aim_x_int} Y:{aim_y_int}",
            (30, 320),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 255),
            2
        )

        cv2.imshow("Vision Sandbox", frame)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


main()
