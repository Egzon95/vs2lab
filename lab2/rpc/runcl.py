import rpc
import logging

from context import lab_logging

def receiveCallback(result_list):
    print("[runcl] Result received in callback: {}".format(result_list.value))

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
# append = cl.AsnycAppend('bar', base_list, cl, receiveCallback)
cl.appenda('bar', base_list, receiveCallback)
cl.alive(13,1)
#result_list = cl.append('bar', base_list)
#print("Result: {}".format(result_list.value))
cl.stop()
