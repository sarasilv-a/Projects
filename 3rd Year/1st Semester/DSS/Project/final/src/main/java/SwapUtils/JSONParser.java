package SwapUtils;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class JSONParser {
    public static JSONArray parseJSONFile(String filePath) throws Exception {
        try (FileReader reader = new FileReader(new File(filePath))) {
            StringBuilder stringBuilder = new StringBuilder();
            int ch;
            while ((ch = reader.read()) != -1) {
                stringBuilder.append((char) ch);
            }
            return new JSONArray(stringBuilder.toString());
        } catch (IOException e) {
            throw new Exception("Error reading the JSON file", e);
        } catch (JSONException e) {
            throw new Exception("Invalid JSON format: " + e.getMessage(), e);
        }
    }
}