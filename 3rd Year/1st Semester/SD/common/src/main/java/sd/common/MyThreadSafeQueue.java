package sd.common;

import java.util.LinkedList;
import java.util.NoSuchElementException;
import java.util.concurrent.locks.ReentrantLock;

public class MyThreadSafeQueue<E> {
    private final LinkedList<E> queue;
    private final ReentrantLock lock;

    public MyThreadSafeQueue() {
        this.queue = new LinkedList<>();
        this.lock = new ReentrantLock();
    }

    public void offer(E item) {
        if (item == null) throw new NullPointerException("Cannot add null to the queue");
        lock.lock();
        try {
            queue.add(item);
        } finally {
            lock.unlock();
        }
    }

    public E poll() {
        lock.lock();
        try {
            if (queue.isEmpty()) {
                return null; // Return null if the queue is empty
            }
            return queue.removeFirst();
        } finally {
            lock.unlock();
        }
    }

    public E peek() {
        lock.lock();
        try {
            if (queue.isEmpty()) {
                return null; // Return null if the queue is empty
            }
            return queue.getFirst();
        } finally {
            lock.unlock();
        }
    }

    public void add(E item) {
        if (item == null) throw new NullPointerException("Cannot add null to the queue");
        lock.lock();
        try {
            queue.add(item);
        } finally {
            lock.unlock();
        }
    }

    public boolean isEmpty() {
        lock.lock();
        try {
            return queue.isEmpty();
        } finally {
            lock.unlock();
        }
    }

    public int size() {
        lock.lock();
        try {
            return queue.size();
        } finally {
            lock.unlock();
        }
    }

    public void clear() {
        lock.lock();
        try {
            queue.clear();
        } finally {
            lock.unlock();
        }
    }

    public void remove(E item) {
        lock.lock();
        try {
            queue.remove(item);
        } finally {
            lock.unlock();
        }
    }
}