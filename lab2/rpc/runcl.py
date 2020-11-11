import rpc
import logging

from context import lab_logging

def receiveCallback(result_list):
    print("[runcl] Result received in callback: {}".format(result_list.value))

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
append = cl.AsnycAppend('bar', base_list, cl, receiveCallback)
print("[runcl] Objects created, starting thread...")
append.start()
cl.alive(13,1)
append.join()
#result_list = cl.append('bar', base_list)
#print("Result: {}".format(result_list.value))

cl.stop()
