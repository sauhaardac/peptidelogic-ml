



import matplotlib.pyplot as plt 
import numpy as np 
import os, subprocess
from matplotlib.backends.backend_pdf import PdfPages 

# default param 
plt.rcParams.update({'font.size': 15})
plt.rcParams['lines.linewidth'] = 2.5 #2.5

def save_figs(filename):
	fn = os.path.join( os.getcwd(), filename)
	pp = PdfPages(fn)
	for i in plt.get_fignums():
		pp.savefig(plt.figure(i))
		plt.close(plt.figure(i))
	pp.close()


def open_figs(filename):
	pdf_path = os.path.join( os.getcwd(), filename)
	if os.path.exists(pdf_path):
		subprocess.call(["xdg-open", pdf_path])


def make_fig():
	fig,ax = plt.subplots()
	ax.grid(True)
	return fig,ax 


def show():
	plt.show()


def plot_instance_over_time_machine(machine_result, fig, ax, color, ax_ylim):

	# TEMP
	temp = True
	if temp:
		events = machine_result # (nframes,) 
		times = np.linspace(0,30,machine_result.size)
	else:
		times = machine_result[:,0]
		events = machine_result[:,1]

	cum_events = np.cumsum(events)

	ax.plot(times,cum_events,color=color)
	ax.set_ylabel(r'$\sum P$')
	ax.set_xlabel('minutes')
	ax.set_ylim(ax_ylim)


def plot_instance_over_time_human(human_result, fig, ax, color, ax_ylim):

	human_result = np.asarray(human_result)

	times = human_result[0][:,0]
	mean_events = np.mean(human_result[:,:,1],axis=0)
	std_events = np.std(human_result[:,:,1],axis=0)
	cum_events = np.cumsum(mean_events)

	ax2 = ax.twinx()
	ax2.plot(times,cum_events,color=color,marker='o')
	ax2.fill_between(times, 
		cum_events-std_events,
		cum_events+std_events,alpha=0.5,color=color)

	ax2.plot(np.nan,np.nan,color=color,marker='o',label='human')
	ax2.plot(np.nan,np.nan,color=color,label='machine')
	ax2.set_ylabel('# events')
	ax2.set_xticks(times)
	ax2.legend(loc = 'upper left')
	ax2.set_ylim(ax_ylim)


def plot_drc_machine(machine_results, fig, ax, colors):

	for dose, machine_result in machine_results.items():

		temp = True
		if temp: 
			# events = machine_result # (nframes,) 
			machine_result = np.asarray(machine_result) # shape = [n cases in drc, n frames]
			times = np.linspace(0,30,machine_result.shape[1])
			mean_events = np.mean(machine_result,axis=0)
			std_events = np.std(machine_result,axis=0)
		else:
			# times = machine_result[:,0]
			# events = machine_result[:,1]
			machine_result = np.asarray(machine_result) # shape = [n cases in drc, n frames, 2]
			times = machine_result[0][:,0]
			mean_events = np.mean(machine_result[:,:,1],axis=0)
			std_events = np.std(machine_result[:,:,1],axis=0)


		cum_events = np.cumsum(mean_events)

		ax.plot(times,cum_events,color=colors[dose],label=dose)
		ax.fill_between(times, 
			cum_events-std_events,
			cum_events+std_events,alpha=0.5,color=colors[dose])		
		ax.set_ylabel(r'$\sum P$')
		ax.set_xlabel('minutes')


def plot_drc_human(human_results, fig, ax, colors):

	ax2 = ax.twinx()

	for dose, human_result in human_results.items():

		human_result = np.asarray(human_result)
		times = human_result[0][:,0]
		mean_events = np.mean(human_result[:,:,1],axis=0)
		std_events = np.std(human_result[:,:,1],axis=0)
		cum_events = np.cumsum(mean_events)

		ax2.plot(times,cum_events,color=colors[dose],marker='o')
		ax2.fill_between(times, 
			cum_events-std_events,
			cum_events+std_events,alpha=0.1,color=colors[dose])

	for dose,color in colors.items():
		ax2.plot(np.nan,np.nan,color=color,label=dose)

	handles, labels = ax2.get_legend_handles_labels()
	labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: int(t[0].split(' ')[0])))
	ax2.legend(handles, labels, loc = 'upper left')
	ax2.set_ylabel('# events')
	ax2.set_xticks(times)



def get_colors(some_dict):

	colors = dict()
	fig,ax = plt.subplots() 
	for key, value in some_dict.items():
		line = ax.plot(np.nan,np.nan)
		colors[key] = line[0].get_color()
	plt.close(fig)
	return colors 