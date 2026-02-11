import java.io.*;
import java.util.*;

public class LogAnalyzer {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("Usage: java LogAnalyzer <logfile>");
            return;
        }
        String logFile = args[0];
        try (BufferedReader br = new BufferedReader(new FileReader(logFile))) {
            String line;
            int suspicious = 0;
            List<String> alerts = new ArrayList<>();
            while ((line = br.readLine()) != null) {
                String lower = line.toLowerCase();
                if (lower.contains("failed login") || lower.contains("error") || 
                    lower.contains("attack") || lower.contains("injection") || 
                    lower.contains("brute") || lower.contains("ransomware")) {
                    suspicious++;
                    alerts.add(line);
                }
            }
            System.out.println("=== Java Log Forensics Report ===");
            System.out.println("Total suspicious entries: " + suspicious);
            if (suspicious > 3) {
                System.out.println("HIGH RISK: Potential incident detected");
            } else {
                System.out.println("Log appears normal.");
            }
            if (!alerts.isEmpty()) {
                System.out.println("\nAlerts:");
                for (String a : alerts) System.out.println(" - " + a);
            }
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
