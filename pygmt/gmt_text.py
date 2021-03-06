import _gmt_structs
import api
from flags import *
import gmt_base_types


class GMT_Text (gmt_base_types.GMT_Resource):
    def register_input(self, input=None):
        #first check if it is a string.  if so, try to open
        #a file with that name 
        if isinstance(input, str) == True:
            self.in_id = self._session.register_io(io_family['textset'], io_method['file'],\
                                          io_geometry['point'], io_direction['in'],\
                                          None, input)
            self.in_str = '-<'+self._session.encode_id(self.in_id)

        #if instead it is a python file object, get the file descriptor
        #number and open with that
        elif isinstance(input, file) == True:
            raise api.GMT_Error("Please give filename instead of open file object")

        #if it is a list of strings, make a GMT_Textset object and register it
        elif isinstance(input, list):
            self.textset = GMT_Textset(self._session, input)
            self.in_id = self._session.register_io(io_family['textset'], io_method['reference'],\
                                          io_geometry['point'], io_direction['in'],\
                                          None, self.textset.ptr)
            self.in_str = '-<'+self._session.encode_id(self.in_id)
        if input == None:
            if self.out_id == -1:
                raise api.GMT_Error("Using empty textset as input")

            data = self._session.retrieve_data(self.out_id)
            self.in_id = self._session.register_io(io_family['textset'], io_method['reference'],\
                                              io_geometry['point'], io_direction['in'], None, data)
            self.in_str = '-<'+self._session.encode_id(self.in_id)

        elif isinstance(input, GMT_Text):
            if input.direction == io_direction['out'] and input.out_id == -1:
                raise api.GMT_Error("Input text empty")
            elif input.direction == io_direction['err']:
                raise api.GMT_Error("Input text empty")
            elif input.direction == io_direction['in']:  #already registered for input
                self.in_id = input.in_id
                self.in_str = input.in_str 
            else:  #registered for output ,reregister as input
                data = self._session.retrieve_data(input.out_id)
                self.in_id = self._session.register_io(io_family['textset'], io_method['reference'],\
                                                       io_geometry['point'], io_direction['in'], None, data)
                self.in_str = '-<'+self._session.encode_id(self.in_id)

        self.direction = io_direction['in']
            

    def register_output(self, output = None):
        if output == None:
            self.out_id = self._session.register_io(io_family['textset'], io_method['duplicate'],\
                                               io_geometry['point'], io_direction['out'], None, None)
            self.out_str = '-bo ->'+self._session.encode_id(self.out_id)

        elif isinstance(output, str) == True:
            self.out_id = self._session.register_io(io_family['textset'], io_method['file'],\
                                               io_geometry['point'], io_direction['out'], None, output)
            self.out_str = '->'+self._session.encode_id(self.out_id)

        elif isinstance(output, file) == True:
            raise api.GMT_Error("Please give filename instead of open file object")

        else:
            raise api.GMT_Error("Text output format not implemented")

        self.direction = io_direction['out']


import sys

class GMT_Textset:
    
    def __init__(self, session, input):
        self._session = session
         # do some type checking
        if isinstance( input, list) == False:
            raise api.GMT_Error("Textset must be given a list of strings")
        for s in input:
            if isinstance(s, str) == False:
                raise api.GMT_Error("Textset must be given a list of strings")
        self.string_list = input
   
        #create the textset using the GMT API
        par = [1,1,len(self.string_list)]
        self.ptr = self._session.create_data( io_family['textset'], io_geometry['point'],\
                                              0, par, None, None, 0, -1, None)
        #assign the memory locations to the internal c strings
        _gmt_structs.gmt_textset_from_string_list(self.ptr, self.string_list)

    def __del__(self):
        _gmt_structs.free_gmt_textset(self.ptr, self.string_list)
        self._session.destroy_data( self.ptr)


