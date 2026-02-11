#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: c_scanner <file_path>\n");
        return 1;
    }
    FILE* f = fopen(argv[1], "rb");
    if (!f) {
        printf("Error opening file\n");
        return 1;
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char* buffer = (unsigned char*)malloc(size);
    fread(buffer, 1, size, f);
    fclose(f);

    int threat = 0;
    char* text = (char*)buffer;
    if (strstr(text, "malware") || strstr(text, "virus") || strstr(text, "exec") || strstr(text, "shell")) threat += 60;
    if (size > 50000) threat += 20;

    printf("=== C Low-Level Scanner Report ===\n");
    printf("File: %s\n", argv[1]);
    printf("Size: %ld bytes\n", size);
    printf("Simulated MD5: a1b2c3d4e5f67890123456789abcdef0\n");
    printf("Threat Score: %d/100\n", threat);
    if (threat > 50) {
        printf("ALERT: Potential threat detected!\n");
    } else {
        printf("Clean.\n");
    }
    free(buffer);
    return 0;
}
