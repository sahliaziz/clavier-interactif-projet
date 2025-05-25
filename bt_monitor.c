#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wiringPi.h>

// Constants
#define LED_PIN 6          // physical pin 22 (wiringPi pin 6)
#define BUTTON_PIN 10       // physical pin 24 (wiringPi pin 10)
#define DEVICE_MAC "XX:XX:XX:XX:XX:XX"
#define CHECK_INTERVAL 10   // seconds

// Function to attempt Bluetooth connection
int connect_bluetooth(const char *mac) {
    char command[128];
    snprintf(command, sizeof(command), "echo -e 'connect %s\nexit' | bluetoothctl > /dev/null", mac);
    return system(command);
}

// Function to check if Bluetooth device is connected
int is_connected(const char *mac) {
    char command[128];
    snprintf(command, sizeof(command), "bluetoothctl info %s | grep 'Connected: yes' > /dev/null", mac);
    return (system(command) == 0);
}

int main() {
    wiringPiSetup();

    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT);
    pullUpDnControl(BUTTON_PIN, PUD_UP); // Button active LOW

    printf("Attempting initial connection...\n");
    connect_bluetooth(DEVICE_MAC);

    while (1) {
        // Check button press
        if (digitalRead(BUTTON_PIN) == LOW) {
            printf("Button pressed. Reconnecting...\n");
            connect_bluetooth(DEVICE_MAC);
            delay(1000);
        }

        // Check connection status
        if (is_connected(DEVICE_MAC)) {
            digitalWrite(LED_PIN, HIGH);
        } else {
            digitalWrite(LED_PIN, LOW);
        }

        sleep(CHECK_INTERVAL);
    }

    return 0;
}
