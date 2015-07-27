import weakref

class HistoryObject(object):
  def __init__(self, value):
    self.value = value;

class Histories(object):
  def __init__(self):
    self._histories = weakref.WeakSet(); 
  
  def register(self, history):
    self._histories.add(history)
    
  def unregister(self, history):
    self._histories.remove(history)

  def _unregister_weak(self, ref):
  #I don't think I need this anymore, but just in case...
    self._histories.data.remove(ref)

  def getHistory(self):
    history = [];
    for h in self._histories:
      history.append(h.value);
    del h #MUST delete this, it's a strong ref
    return history; 