import types

from streams import video_stream as vs


def test_videostream_nextframe_and_end(monkeypatch):
    """
    Testa que:
      - nextFrame() devolve bytes para alguns frames
      - frameNbr() incrementa
      - devolve None no fim do "ficheiro"
    sem usar OpenCV real.
    """

    # frames "crus" que o VideoCapture vai devolver
    raw_frames = [b"FRAME1", b"FRAME2"]

    class DummyCap:
        def __init__(self, filename):
            self.filename = filename
            self.frames = raw_frames.copy()
            self.released = False

        def isOpened(self):
            return True

        def read(self):
            if self.frames:
                frame = self.frames.pop(0)
                return True, frame
            else:
                return False, None

        def release(self):
            self.released = True

    class DummyEncoded:
        def __init__(self, data: bytes):
            self._data = data

        def tobytes(self):
            # simulamos o .tobytes() do numpy array
            return self._data

    def fake_VideoCapture(filename):
        return DummyCap(filename)

    def fake_imencode(ext, frame):
        # frame aqui é o que veio de DummyCap.read()
        return True, DummyEncoded(frame)

    # Criar um "módulo" cv2 fake e injectá-lo no módulo video_stream
    dummy_cv2 = types.SimpleNamespace(
        VideoCapture=fake_VideoCapture,
        imencode=fake_imencode,
    )
    monkeypatch.setattr(vs, "cv2", dummy_cv2, raising=False)

    # 2) Instanciar VideoStream com o dummy cv2
    vs_obj = vs.VideoStream("dummy-file")

    # Primeiro frame
    f1 = vs_obj.nextFrame()
    assert f1 == b"FRAME1"

    # Segundo frame
    f2 = vs_obj.nextFrame()
    assert f2 == b"FRAME2"

    # Depois acaba -> None
    f3 = vs_obj.nextFrame()
    assert f3 is None

    # frameNbr deve ser 2
    assert vs_obj.frameNbr() == 2

    # release não rebenta
    vs_obj.release()
    assert vs_obj.videoCapture.released is True
