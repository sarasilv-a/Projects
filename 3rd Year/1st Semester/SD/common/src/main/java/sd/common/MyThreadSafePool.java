package sd.common;

import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class MyThreadSafePool {

    private final int poolSize;
    private final Thread[] workers;
    private final Queue<Runnable> taskQueue;
    private final Lock lock;
    private final Condition notEmpty;
    private volatile boolean isRunning;

    public MyThreadSafePool(int poolSize) {
        this.poolSize = poolSize;
        this.taskQueue = new LinkedList<>();
        this.lock = new ReentrantLock();
        this.notEmpty = lock.newCondition();
        this.isRunning = true;

        this.workers = new Thread[poolSize];
        for (int i = 0; i < poolSize; i++) {
            workers[i] = new Worker("MyThreadSafePool-Worker-" + i);
            workers[i].start();
        }
    }

    public void submit(Runnable task) {
        lock.lock();
        try {
            taskQueue.add(task);
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }

    public void shutdown() {
        isRunning = false;
        lock.lock();
        try {
            notEmpty.signalAll();
        } finally {
            lock.unlock();
        }
    }

    private class Worker extends Thread {
        public Worker(String name) {
            super(name);
        }

        @Override
        public void run() {
            while (isRunning) {
                Runnable task;
                lock.lock();
                try {
                    while (taskQueue.isEmpty() && isRunning) {
                        try {
                            notEmpty.await();
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                        }
                    }
                    if (!isRunning) break;
                    task = taskQueue.poll();
                } finally {
                    lock.unlock();
                }
                try {
                    if (task != null) {
                        task.run();
                    }
                } catch (RuntimeException e) {
                    System.err.println("Task execution failed: " + e.getMessage());
                }
            }
        }
    }
}

