#include <Wifi.h>
#include <random>
#include <iostream>
#include <cstdlib>
#include <ctime>

// change these
const char *ssid = "HANSHAKE-LAB-AP";
const char *password = "password";

void setup()
{
    Serial.begin(115200);
    std::srand(esp_random());

    // random addresses
    int octet1 = (std::rand() % (253 - 3 + 1)) + 3;
    int octet2 = (std::rand() % (253 - 3 + 1)) + 3;
    int octet3 = (std::rand() % (253 - 3 + 1)) + 3;

    IPAddress localIP(octet1, octet2, octet3, 1);
    IPAddress gateway(octet1, octet2, octet3, 1);
    IPAddress subnet(255, 255, 255, 0);

    Serial.printf("AP SSID: %s\n", ssid);
    Serial.printf("AP IP: %s\n", localIP.toString().c_str());

    WiFi.softAPConfig(localIP, gateway, subnet);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, password);

    Serial.println("Lab is starting...");
}

void loop()
{
    delay(10);
}
