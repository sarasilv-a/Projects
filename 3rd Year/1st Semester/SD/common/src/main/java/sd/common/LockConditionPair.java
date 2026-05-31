package sd.common;

import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public class LockConditionPair {
    private final ReentrantLock lock;
    private final Condition condition;
    public LockConditionPair() {
        this.lock = new ReentrantLock();
        this.condition = lock.newCondition();
    }
    public void lock() {
        lock.lock();
    }
    public void unlock() {
        lock.unlock();
    }
    public void await() throws InterruptedException {
        condition.await();
    }
    public void signalAll() {
        condition.signalAll();
    }
}
