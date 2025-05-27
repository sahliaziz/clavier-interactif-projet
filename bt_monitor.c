#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <gpiod.h>
#include <time.h>

#define CHIP_NAME "gpiochip0"
#define BUTTON_LINE 11
#define LED_LINE 25

#define BT_MAC "DA:FE:25:0E:EE:19"
#define CHECK_INTERVAL 10  // seconds

// Connect to the Bluetooth speaker using bluetoothctl
void connect_bluetooth(const char *mac) {
    char command[128];
    snprintf(command, sizeof(command), "echo 'connect %s\nexit\n' | bluetoothctl > /dev/null", mac);
    system(command);
}

// Check if the Bluetooth speaker is connected
int is_connected(const char *mac) {
    char command[128];
    snprintf(command, sizeof(command), "bluetoothctl info %s | grep 'Connected: yes' > /dev/null", mac);
    return (system(command) == 0);
}

int main() {
    struct gpiod_chip *chip;
    struct gpiod_line *button, *led;
    int ret;

    chip = gpiod_chip_open_by_name(CHIP_NAME);
    if (!chip) {
        perror("Open chip failed");
        return 1;
    }

    button = gpiod_chip_get_line(chip, BUTTON_LINE);
    led = gpiod_chip_get_line(chip, LED_LINE);

    if (!button || !led) {
        perror("Get line failed");
        return 1;
    }

    // Request input (button) with bias pull-up
    ret = gpiod_line_request_input_flags(button, "bt_button", GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP);
    if (ret < 0) {
        perror("Request button input failed");
        return 1;
    }

    // Request output (LED)
    ret = gpiod_line_request_output(led, "bt_led", 0);
    if (ret < 0) {
        perror("Request LED output failed");
        return 1;
    }

    printf("Attempting initial connection...\n");
    connect_bluetooth(BT_MAC);
    if (is_connected(BT_MAC)) printf("Connected successfully\n");

    while (1) {
        int value = gpiod_line_get_value(button);
        if (value == 0) {  // button pressed (active low)
            printf("Button pressed: reconnecting...\n");
            if (is_connected(BT_MAC)) {
                printf("Already connected.\n");
            } else {
                printf("Connecting to Bluetooth speaker...\n");
                connect_bluetooth(BT_MAC);
            sleep(1); // debounce delay
            }
        }

        if (is_connected(BT_MAC)) {
            gpiod_line_set_value(led, 1);
        } else {
            gpiod_line_set_value(led, 0);
        }

        sleep(CHECK_INTERVAL);
    }

    gpiod_chip_close(chip);
    return 0;
}
