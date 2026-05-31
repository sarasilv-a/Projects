package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class AuthResponse extends Message{
    private int clientID;

    public AuthResponse() {
        super(0, AuthResponse.class.getName());
        this.clientID = 0;
    }

    public AuthResponse(int clientID) {
        super(clientID, AuthResponse.class.getName());
        this.clientID = clientID;
    }

    public int getClientID() {
        return this.clientID;
    }

    @Override
    protected void serializeSubclass(DataOutputStream output) throws IOException {
        output.writeInt(clientID);
    }

    protected Message deserializeSubclass(DataInputStream input, int clientID) throws IOException {
        int readClientID = input.readInt();
        return new AuthResponse(readClientID);
    }

    public String toString() {
        return super.toString() + "AuthResponse{" + "clientID=" + this.clientID + '}';
    }
}
