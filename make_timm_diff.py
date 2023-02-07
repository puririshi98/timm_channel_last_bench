import timm
import subprocess
def make_diff(x):
	tru_dict = {}
	false_dict = {}
	for (model, amp, chanlast), sampersec in x.items():
		if "True" in chanlast:
			tru_dict[(model, amp)] = float(sampersec)
		else:
			false_dict[(model, amp)] = float(sampersec)
	print("perf diff w/ channels last:", {key:(tru_dict[key]-false_dict[key])/false_dict[key] for key in tru_dict.keys()})

samples_per_sec = {}
for amp in [False, True]:
	for model_name in timm.list_models():
		for channels_last  in [False, True]:
			key = ('model=' + str(model_name), 'amp=' + str(amp), 'channels-last=' + str(channels_last))
			print("running ", key)
			cmd = 'python3 benchmark.py  -b 1 --model ' + str(model_name) + (' --amp' if amp else '') + (' --channels-last' if channels_last else '')
			try:
				p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			except:
				print(cmd.split())
			out, err = p.communicate()
			lines = str(out.decode()).splitlines()
			for line in lines:
				if 'train_samples_per_sec' in line:
					time = float(line.split(':')[-1][:-1])
					break
			try:
				samples_per_sec[key] = time
				print('train_samples_per_sec:', time)
				#print('running_dict:', samples_per_sec)
				del time
			except:
				contin = False
				for line in lines:
					if 'Unknown model' in line:
						print(line)
						contin = True
				if contin:
					continue
				else:
					for line in lines:
						print(line)
					for line in str(err.decode()).splitlines():
						print(line)
		make_diff(samples_per_sec)
