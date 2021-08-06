import lldb
import sys
import traceback

def printException():
    eInfo = sys.exc_info()
    print ("Exception:")
    print (traceback.print_tb(eInfo[2], 1))
    print (eInfo[0], eInfo[1] )
    return

def QUrl_SummaryProvider(valobj, internal_dict):
   return valobj.GetFrame().EvaluateExpression(valobj.GetName() + '.toString((QUrl::FormattingOptions)QUrl::PrettyDecoded)');

def QString_SummaryProvider(valobj, internal_dict):
   def make_string_from_pointer_with_offset(F,OFFS,L):
       strval = 'u"'
       try:
           data_array = F.GetPointeeData(0, L).uint16
           OFFS = int(OFFS)
           for X in range(OFFS, L):
               V = data_array[X]
               if V == 0:
                   break
               strval += chr(V)
       # Ignore index error because if you set breakpoint on a line that constructs a QString
       # it has not yet been defined and you end up with an IndexError unable to read data_array
       except(IndexError):
           pass
       except:
           printException()
           pass
       strval = strval + '"'
       return strval.encode('utf-8')

   #qt5
   def qstring_summary(value):
       try:
           d = value.GetChildMemberWithName('d')
           #have to divide by 2 (size of unsigned short = 2)
           offset = d.GetChildMemberWithName('offset').GetValueAsUnsigned() / 2
           size = get_max_size(value)
           return make_string_from_pointer_with_offset(d, offset, size)
       except:
           printException()
           return value

   def get_max_size(value):
       _max_size_ = None
       try:
           debugger = value.GetTarget().GetDebugger()
           _max_size_ = int(lldb.SBDebugger.GetInternalVariableValue('target.max-string-summary-length', debugger.GetInstanceName()).GetStringAtIndex(0))
       except:
           _max_size_ = 512
       return _max_size_
   return qstring_summary(valobj)

class QVector_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
            self.valobj = valobj

    def num_children(self):
            try:
                    s = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('size').GetValueAsUnsigned()
                    return s
            except:
                    return 0;

    def get_child_index(self,name):
            try:
                    return int(name.lstrip('[').rstrip(']'))
            except:
                    return None

    def get_child_at_index(self,index):
            if index < 0:
                    return None
            if index >= self.num_children():
                    return None
            if self.valobj.IsValid() == False:
                    return None
            try:
                    doffset = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('offset').GetValueAsUnsigned()
                    type = self.valobj.GetType().GetTemplateArgumentType(0)
                    elementSize = type.GetByteSize()
                    return self.valobj.GetChildMemberWithName('d').CreateChildAtOffset('[' + str(index) + ']', doffset + index * elementSize, type)
            except:
                    return None

class QList_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
            self.valobj = valobj

    def num_children(self):
            try:
                    listDataD = self.valobj.GetChildMemberWithName('p').GetChildMemberWithName('d')
                    begin = listDataD.GetChildMemberWithName('begin').GetValueAsUnsigned()
                    end = listDataD.GetChildMemberWithName('end').GetValueAsUnsigned()
                    return (end - begin)
            except:
                    return 0;

    def get_child_index(self,name):
            try:
                    return int(name.lstrip('[').rstrip(']'))
            except:
                    return None

    def get_child_at_index(self,index):
            if index < 0:
                    return None
            if index >= self.num_children():
                    return None
            if self.valobj.IsValid() == False:
                    return None
            try:
                    pD = self.valobj.GetChildMemberWithName('p').GetChildMemberWithName('d');
                    pBegin = pD.GetChildMemberWithName('begin').GetValueAsUnsigned()
                    pArray = pD.GetChildMemberWithName('array').GetValueAsUnsigned()
                    pAt = pArray + pBegin + index
                    type = self.valobj.GetType().GetTemplateArgumentType(0)
                    elementSize = type.GetByteSize()
                    voidSize = pD.GetChildMemberWithName('array').GetType().GetByteSize()
                    return self.valobj.GetChildMemberWithName('p').GetChildMemberWithName('d').GetChildMemberWithName('array').CreateChildAtOffset('[' + str(index) + ']', pBegin + index * voidSize, type)
            except:
                    printException()
                    return None

class QPointer_SyntheticProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj

    def num_children(self):
        try:
            wp = self.valobj.GetChildMemberWithName('wp')
            d = wp.GetChildMemberWithName('d')
            if d.GetValueAsUnsigned() == 0 or d.GetChildMemberWithName('strongref').GetChildMemberWithName('_q_value').GetValueAsUnsigned() == 0 or wp.GetChildMemberWithName('value').GetValueAsUnsigned() == 0:
                return 0
            else:
                return 1
        except:
            return 0;

    def get_child_index(self,name):
        return 0

    def get_child_at_index(self,index):
        if index < 0:
            return None
        if index >= self.num_children():
            return None
        if self.valobj.IsValid() == False:
            return None
        try:
            type = self.valobj.GetType().GetTemplateArgumentType(0)
            return self.valobj.GetChildMemberWithName('wp').GetChildMemberWithName('value').CreateChildAtOffset('value', 0, type)
        except:
            printException()
            return None




class QMap_SyntheticProvider:
    def __init__(self, valobj, dict):
        self.valobj = valobj
        self.garbage = False
        self.root_node = None
        self.header = None
        self.data_type = None

    def num_children(self):
        return self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('size').GetValueAsUnsigned(0)

    def get_child_index(self, name):
        try:
            return int(name.lstrip('[').rstrip(']'))
        except:
            return -1

    def get_child_at_index(self, index):
        if index < 0:
            return None
        if index >= self.num_children():
            return None
        if self.garbage:
            return None
        try:
            offset = index
            current = self.header
            while offset > 0:
                current = self.increment_node(current)
                offset -= 1
            child_data = current.Dereference().Cast(self.data_type).GetData()
            return current.CreateValueFromData('[' + str(index) + ']', child_data, self.data_type)
        except:
            return None

    def extract_type(self):
        map_type = self.valobj.GetType().GetUnqualifiedType()
        target = self.valobj.GetTarget()
        if map_type.IsReferenceType():
            map_type = map_type.GetDereferencedType()
        if map_type.GetNumberOfTemplateArguments() > 0:
            first_type = map_type.GetTemplateArgumentType(0)
            second_type = map_type.GetTemplateArgumentType(1)
            close_bracket = '>'
            if second_type.GetNumberOfTemplateArguments() > 0:
                close_bracket = ' >'
            data_type = target.FindFirstType(
                'QMapNode<' + first_type.GetName() + ', ' + second_type.GetName() + close_bracket)
        else:
            data_type = None
        return data_type

    def node_ptr_value(self, node):
        return node.GetValueAsUnsigned(0)

    def right(self, node):
        return node.GetChildMemberWithName('right')

    def left(self, node):
        return node.GetChildMemberWithName('left')

    def parent(self, node):
        parent = node.GetChildMemberWithName('p')
        parent_val = parent.GetValueAsUnsigned(0)
        parent_mask = parent_val & ~3
        parent_data = lldb.SBData.CreateDataFromInt(parent_mask)
        return node.CreateValueFromData('parent', parent_data, node.GetType())

    def increment_node(self, node):
        max_steps = self.num_children()
        if self.node_ptr_value(self.right(node)) != 0:
            x = self.right(node)
            max_steps -= 1
            while self.node_ptr_value(self.left(x)) != 0:
                x = self.left(x)
                max_steps -= 1
                if max_steps <= 0:
                    self.garbage = True
                    return None
            return x
        else:
            x = node
            y = self.parent(x)
            max_steps -= 1
            while self.node_ptr_value(x) == self.node_ptr_value(self.right(y)):
                x = y
                y = self.parent(y)
                max_steps -= 1
                if max_steps <= 0:
                    self.garbage = True
                    return None
            if self.node_ptr_value(self.right(x)) != self.node_ptr_value(y):
                x = y
            return x

    def update(self):
        try:
            self.garbage = False
            self.root_node = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName(
                'header').GetChildMemberWithName('left')
            self.header = self.valobj.GetChildMemberWithName('d').GetChildMemberWithName('mostLeftNode')
            self.data_type = self.extract_type()
        except:
            pass

    def has_children(self):
        return True