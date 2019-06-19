def conbine():
    page_id = {}
    o1 = open('question_list.txt', 'w')
    for file in ['q3.txt', 'q4.txt', 'q2.txt', 'q1.txt']:
        with open(file) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line_split = line.strip().split()
                try:
                    if(line_split[0].split('/')[2] not in page_id):
                        #print(line_split[0].split('/')[2])
                        page_id[line_split[0].split('/')[2]] = True
                        o1.write(line)
                        if(len(page_id)%10000==0):
                            print(len(page_id))
                except:
                    print(line)


if __name__ == '__main__':
    conbine()

