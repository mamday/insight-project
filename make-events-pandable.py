import sys

def main():
  in_file = sys.argv[1]
  e_list,ss_e_list,info = parse_event_file(in_file)
  print ','.join(['evt_id','evt_url','evt_name','fee','duration','date','time','lat','lon'])
 
  for entry in xrange(len(info['evt_url'])):
    print ','.join([str(entry),info['evt_url'][entry],info['evt_name'][entry],info['fee'][entry],info['duration'][entry],info['date'][entry],info['time'][entry],info['lat'][entry],info['lon'][entry]])

  
def parse_event_file(in_file):
  evt_list = []
  space_split_evt_list = []
  info_dict = {'evt_url':[],'evt_name':[],'fee':[],'duration':[],'date':[],'time':[],'lat':[],'lon':[]}
  for line in open(in_file).readlines():
    cur_split = line.split(',')
    if(cur_split[0]=="Event Description"):
      cur_text =  ''.join(cur_split[1:])
      evt_list.append(cur_text)
      space_split_evt_list.append(cur_split)
    if(cur_split[0]=="Event Info"):
      info_dict['evt_url'].append(cur_split[1])
      info_dict['evt_name'].append(cur_split[2])
      info_dict['fee'].append(cur_split[-6])
      info_dict['duration'].append(cur_split[-5])
      info_dict['date'].append(cur_split[-4])
      info_dict['time'].append(cur_split[-3])
      info_dict['lat'].append(cur_split[-2])
      if(not('\n' in cur_split[-1])):
        print 'Danger!',cur_split[-1]
      info_dict['lon'].append(cur_split[-1].rstrip())

  return evt_list,space_split_evt_list,info_dict

if __name__=="__main__":
  main()

