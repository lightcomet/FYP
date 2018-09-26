from subprocess import check_output
output = check_output(['hostname', '-I']).decode("utf-8")
output = output.replace('\n','a')
output = output.replace(' ','a')
output = output.replace('a','\n')
print(output) #2 \n is behind the last ip address