# trying to talk bluetooth but this adafruit library just isnt doing what i hoped.
# probbaly going to delete this.


from adafruit_ble import BLERadio
from pprint import pprint
from adafruit_ble.advertising import decode_data
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
import asyncio

ble = BLERadio()
print("anything connected? ", ble.connected)

async def scan():

   print("scanning")
   found = set()
   scan_responses = set()
   connected = list()
  
   
   for i in [1,2,3,4,5,6,7,8]:
       print("scan ", i)
       scan_results = ble.start_scan(ProvideServicesAdvertisement,timeout=5)
       await asyncio.sleep(0)
       for advertisement in scan_results:
          addr = advertisement.address
          print("device  address: ", addr)
          if advertisement.complete_name:       
             print("device  name: ", advertisement.complete_name) 
             if advertisement.complete_name == 'JBL Flip 3':
                print("found ", advertisement.complete_name)
                print("anything connected? ", ble.connected)
          
                # try:
                   # conn = ble.connect(addr)
                # except Exception as e:
                   #  print('oops, connect error', e)
                # else:
                   # print('connected!?', conn.connected)
                   # connected.append(advertisement.complete_name)
            
          if advertisement.scan_response and addr not in scan_responses:
              pprint(advertisement.scan_response)
              scan_responses.add(addr)
          elif not advertisement.scan_response and addr not in found:
              found.add(addr)
          else:
              continue
      
          print("found:", addr) 
          print("scan responses: ", scan_responses)
          # pprint(decode_data(advertisement.data))
          # print("\t" + repr(advertisement))
          print("connected: ", connected)
      
          print()
       print(ble.connections)
   
   
   print("scan done")
   print("connected to ", connected[0] if len(connected) > 0 else 'nothing')
   print(found)
   print(scan_responses)
   return connected

asyncio.run(scan())

