from multiprocessing import Process, Queue
import writer
import reader

if __name__ == "__main__":
    queue = Queue()

    writer_process = Process(target=writer.run_writer, args=(queue,))
    reader_process = Process(target=reader.run_reader, args=(queue,))

    writer_process.start()
    reader_process.start()

    writer_process.join()
    reader_process.join()
