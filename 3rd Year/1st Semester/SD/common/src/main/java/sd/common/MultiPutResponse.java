package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
public class MultiPutResponse extends Message {
    private boolean success;

    public MultiPutResponse() {
        super(0, MultiPutResponse.class.getName());
        this.success = false;
    }

    public MultiPutResponse(int clientID, boolean success) {
        super(clientID, MultiPutResponse.class.getName());
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
        return new MultiPutResponse(clientID, success);
    }

    @Override
    public String toString() {
        return super.toString() + " MultiPutResponse{" + "success=" + success + '}';
    }
}
