package SwapUtils;

import org.json.JSONObject;

import java.io.FileWriter;
import java.io.IOException;

public class JSONWriter {
    public static void writeJSONToFile(JSONObject jsonObject, String filePath) throws Exception {
        try (FileWriter file = new FileWriter(filePath)) {
            file.write(jsonObject.toString(4)); // Indenta com 4 espaços para melhor leitura
        } catch (IOException e) {
            throw new Exception("Error writing JSON to file: " + e.getMessage(), e);
        }
    }
}