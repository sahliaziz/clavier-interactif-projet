#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <gpiod.h>

// Define constants
#define GPIO_CHIP "/dev/gpiochip0"
#define GPIO_LINE 25
#define BT_DEVICE_MAC "DA:FE:25:0E:EE:19"
#define CHECK_INTERVAL 10

// Function to check if the Bluetooth device is connected
int is_device_connected(const char *mac_address) {
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "bluetoothctl info %s | grep -q 'Connected: yes'", mac_address);
    return (system(cmd) == 0);
}

int main() {
    struct gpiod_chip *chip;
    struct gpiod_line *line;
    int last_status = -1;

    chip = gpiod_chip_open(GPIO_CHIP);
    if (!chip) {
        perror("Failed to open GPIO chip");
        return 1;
    }

    line = gpiod_chip_get_line(chip, GPIO_LINE);
    if (!line) {
        perror("Failed to get GPIO line");
        gpiod_chip_close(chip);
        return 1;
    }

    if (gpiod_line_request_output(line, "bt_led_control", 0) < 0) {
        perror("Failed to request GPIO line as output");
        gpiod_chip_close(chip);
        return 1;
    }

    while (1) {
        int connected = is_device_connected(BT_DEVICE_MAC);
        if (connected != last_status) {
            gpiod_line_set_value(line, connected ? 1 : 0);
            printf("Bluetooth device %s %s\n", BT_DEVICE_MAC, connected ? "connected" : "disconnected");
            last_status = connected;
        }
        sleep(CHECK_INTERVAL);
    }

    gpiod_line_release(line);
    gpiod_chip_close(chip);
    return 0;
}
