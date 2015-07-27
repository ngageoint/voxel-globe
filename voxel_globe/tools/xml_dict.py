import xml.etree.ElementTree as ElementTree

class XmlList(list):
  def find_at(self, **kwargs):
    ''' attributname__is = value '''
    
    results = list(self)
    for (key, value) in kwargs.iteritems():
      (name, cmd) = key.split('__');
      if cmd == 'is':
        cmd = lambda x: x==value;
      elif cmd == 'iis':
        value = value.lower()
        cmd = lambda x: x.lower()==value;
      elif cmd == 'contains':
        cmd = lambda x: value in x;
      elif cmd == 'icontains':
        value = value.lower()
        cmd = lambda x: value in x.lower();
      elif cmd == 'startswith':
        cmd = lambda x: x.startswith(value);
      elif cmd == 'istartswith':
        value = value.lower()
        cmd = lambda x: x.lower().startswith(value);
      elif cmd == 'endswith':
        cmd = lambda x: x.endswith(value);
      elif cmd == 'iendswith':
        value = value.lower()
        cmd = lambda x: x.lower().endswith(value);
      else:
        raise Exception('Unknown command %s' % cmd)
      
      for x in range(len(results)-1, -1, -1):
        if not cmd(self[x].at[name]):
          results.pop(x);

    return results;
  def __repr__(self, indent=0):
    s = '';
    for l in self:
      s += l.__repr__(indent+2) + '\n';
    return s[:-1];

class XmlDictConfig(dict):
    '''
    Based off of
    http://code.activestate.com/recipes/410469-xml-as-dictionary/
    
    But BETTER, but a quick hack. This is still VERY hacky. 
    
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
      self.at = dict();
      self.text = None;

      if parent_element.items():
      #If it has attributes
        self.at.update(dict(parent_element.items()))
        #at to attribute dict
      for element in parent_element:
        if len(element):
          # treat like dict - we assume that if the first two tags
          # in a series are different, then they are all different.
          if len(element) == 1 or element[0].tag != element[1].tag:
            aDict = XmlDictConfig(element)
          # treat like list - we assume that if the first two tags
          # in a series are the same, then the rest are the same.
          #BUG I'm pretty sure this will BREAK if the tags are in mixed
          #    order, but I don't currently care
          else:
            # here, we put the list in dictionary; the key is the
            # tag name the list elements all share in common, and
            # the value is the list itself 
            #aDict = {element[0].tag: XmlListConfig(element)}
            aDict = XmlListConfig(element)
          # if the tag has attributes, add those to the dict
          if element.items():
            aDict.at.update(dict(element.items()))
          if element.text:
            aDict.text = element.text; 
          self.update({element.tag: aDict})
        # this assumes that if you've got an attribute in a tag,
        # you won't be having any text. This may or may not be a 
        # good idea -- time will tell. It works for the way we are
        # currently doing XML configuration files...
        elif element.items() or element.text:
          #self.update({element.tag: dict(element.items())}) #WRONG
          self.update({element.tag: XmlDictConfig(element)})
#          self.at = dict(element.items())
        # finally, if there are no child tags and no attributes, extract
        # the text
#        else:
#          self.update({element.tag: element.text}) #ALSO WRONG
    def __repr__(self, indent=0):
      s = '';
      if self.at:
        s += ' '*indent+'@: '+str(self.at) + '\n';
      if self.text:
        s += ' '*indent+'T: '+self.text + '\n';
      for (key, value) in self.iteritems():
        s += ' '*indent + key + '\n'
        s += value.__repr__(indent+2) + '\n';
      return s[:-1];
      

class XmlListConfig(XmlDictConfig):
    ''' http://code.activestate.com/recipes/410469-xml-as-dictionary/ '''
    def __init__(self, aList):
        self.at = dict()
        self.text = None;
        if aList.items():
          self.at.update(dict(aList.items()))
#        print "It's ", aList
        eList = XmlList();
        for element in aList:
#            print element, len(element)
#            eList.append(XmlDictConfig(element))
#            print len(element) 
#            if len(element) == 1 or element[0].tag != element[1].tag:
#              eList.append(XmlDictConfig(element))
#            else:
#              eList.append(XmlListConfig(element))
#            '''
#            print element, len(element)
            if len(element):
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                  eList.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                  eList.append(XmlListConfig(element))
            elif element.items:
              eList.append(XmlDictConfig(element))
            elif element.text:
              text = element.text.strip()
              if text:
                eList.append(text)
#        print aList[0].tag
#        print eList'''
        self.update({aList[0].tag: eList})

def load_xml(xml_filename):
  tree = ElementTree.parse(xml_filename)
  root = tree.getroot()
  return XmlDictConfig(root)