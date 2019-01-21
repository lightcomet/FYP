from subprocess import check_output
output = check_output(['hostname', '-I']).decode("utf-8")
output = output.replace('\n','a')
output = output.replace(' ','a')
output = output.replace('a','\n')
output = output[:-2] # remove last 2 characters as 2 '\n' are behind the ip address
print(output)
