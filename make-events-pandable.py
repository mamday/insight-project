import sys

def main():
  in_file = sys.argv[1]
#Events
  if('event' in sys.argv[2]):
    e_list,ss_e_list,info = parse_event_file(in_file)
    if(sys.argv[2]=='eventinfo'):
      print ','.join(['evt_id','evt_url','evt_name','fee','duration','date','time','lat','lon'])
      for entry in xrange(len(info['evt_url'])):
        print ','.join([str(entry),info['evt_url'][entry],'"'+info['evt_name'][entry]+'"',info['fee'][entry],info['duration'][entry],info['date'][entry],info['time'][entry],info['lat'][entry],info['lon'][entry]])
    elif(sys.argv[2]=='eventdesc'): 
      print ','.join(['evt_id','evt_description'])
      for ind,desc in enumerate(e_list):
        print ind,',"',desc.rstrip(),'"' 
    else:
      print 'Invalid Entry'

#Groups
  elif(sys.argv[2]=='group'):
    info = parse_group_file(in_file)
    print ','.join(['group_id','group_url','group_name','topic'])
    for entry in xrange(len(info['group_url'])):
      print ','.join([str(entry),info['group_url'][entry],'"'+info['group_name'][entry]+'"',info['topic'][entry]]) 
  else:
    print 'Invalid Entry'

def parse_group_file(in_file):
  info_dict = {'group_url':[],'group_name':[],'topic':[]}
  for line in open(in_file).readlines():
    cur_split = line.split(',')
    info_dict['group_url'].append(cur_split[-3]) 
    info_dict['group_name'].append(cur_split[1]) 
    info_dict['topic'].append(cur_split[5]) 
  return info_dict

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

