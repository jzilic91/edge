from utilities import OffloadingSiteCode
from mobile_device import MobileDevice
from offloading_site import OffloadingSite
from data_provider import DataProvider

NUMBER_OF_SAMPLINGS = 1
NUMBER_OF_APP_EXECUTIONS = 100000

if __name__ == "__main__":

	# data provider will parse all failures from data file which contains failure trace logs
	data_provider = DataProvider('pnnl07_raw/clean-output.csv')

	# declare mobile device with offloading sites included in the simulation and data provider
	mobile_device = MobileDevice((OffloadingSite(5000, 8, 300, OffloadingSiteCode.EDGE_DATABASE_SERVER, data_provider.get_fat_node_failure_provider(), 'A'), \
		OffloadingSite(8000, 8, 150, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, data_provider.get_thin_node_failure_provider(), 'A'),  \
		OffloadingSite(5000, 8, 150, OffloadingSiteCode.EDGE_REGULAR_SERVER, data_provider.get_other_thin_node_failure_provider(), 'A')), \
		OffloadingSite(20000, 128, 1000, OffloadingSiteCode.CLOUD_DATA_CENTER, data_provider.get_lustre_server_failure_provider(), 1))

	# mobile_device.deploy_facebook_application()
	# mobile_device.deploy_chess_application()
	mobile_device.deploy_facerecognizer_application()
	mobile_device.deploy_network_model()
	# mobile_device.print_entire_config()

	mobile_device.deploy_efpo_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_energy_efficient_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_mobile_cloud_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_local_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_chess_application()

	mobile_device.deploy_efpo_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_energy_efficient_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_mobile_cloud_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_local_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_facebook_application()

	mobile_device.deploy_efpo_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_energy_efficient_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_mobile_cloud_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.deploy_local_ode()
	mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, False)

	mobile_device.plot_statistics()

	# mobile_device.deploy_facebook_application()
	# mobile_device.deploy_network_model()
	# mobile_device.deploy_efpo_ode()
	# mobile_device.run(NUMBER_OF_SAMPLINGS, NUMBER_OF_APP_EXECUTIONS, True)
	# mobile_device.plot_statistics()