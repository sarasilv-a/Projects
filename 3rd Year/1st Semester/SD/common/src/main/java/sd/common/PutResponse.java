package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class PutResponse extends Message {
    private boolean success;

    public PutResponse() {
        super(0, PutResponse.class.getName());
        this.success = false;
    }

    public PutResponse(int clientID, boolean success) {
        super(clientID, PutResponse.class.getName());
        this.success = success;
    }

    public boolean isSuccess() {
        return success;
    }

    @Override
    protected void serializeSubclass(DataOutputStream out) throws IOException {
        out.writeBoolean(success);
    }

    @Override
    protected Message deserializeSubclass(DataInputStream in, int clientID) throws IOException {
        boolean success = in.readBoolean();
        return new PutResponse(clientID, success);
    }

    @Override
    public String toString() {
        return super.toString() + " PutResponse{" + "success=" + success + '}';
    }
}
