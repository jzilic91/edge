from utilities import OffloadingSiteCode, DatasetType
from mobile_device import MobileDevice
from offloading_site import OffloadingSite
from data_provider import DataProvider
from data_storage import DataStorage


def main():
	# data storage will parse all failures from LANL data file which contains failure trace logs
	data_storage = DataStorage("../data/LA-UR-05-7318-failure-data-1996-2005.csv", DatasetType.LANL_DATASET)

	number_of_samplings = 10000
	number_of_app_executions = 40

	ec_node_candidate_list = [(19, 1), (19, 11), (19, 4), (19, 8), (20, 41)]
	ed_node_candidate_list = [(1, 0), (5, 158), (5, 165), (5, 243), (5, 48), (7, 1), (7, 154), (7, 242), (7, 32)]
	er_node_candidate_list = [(3, 0), (16, 80), (4, 55), (4, 1), (4, 3)]
	cd_node_candidate_list = [(22, 0)]
	# ec_node_candidate_list = [(19, 8)]
	# ed_node_candidate_list = [(5, 243)]
	# er_node_candidate_list = [(4, 1)]
	# cd_node_candidate_list = [(22, 0)]

	application_names = ['ANTIVIRUS', 'GPS_NAVIGATOR', 'CHESS', 'FACEBOOK', 'FACERECOGNIZER']
	mixed_mode = True
	sensitivity_analysis = False
		# NodeCategory.EC_DATA: [(19, 1)],
		# NodeCategory.ED_DATA: [(1, 0)],
		# NodeCategory.ER_DATA: [(3, 0)],
		# NodeCategory.CD_DATA: [(22, 0)]
	#}

	for i in range(5):
		# declare mobile device with offloading sites included in the simulation and data provider
		ec_node_candidate = ec_node_candidate_list[i]
		ed_node_candidate = ed_node_candidate_list[i]
		er_node_candidate = er_node_candidate_list[i]
		cd_node_candidate = cd_node_candidate_list[0]
		application = application_names[i]

		print('EC node candidate: ' + str(ec_node_candidate))
		print('ED node candidate: ' + str(ed_node_candidate))
		print('ER node candidate: ' + str(er_node_candidate))
		print('CD node candidate: ' + str(cd_node_candidate))

		edge_data_site = OffloadingSite(5000, 8, 300, OffloadingSiteCode.EDGE_DATABASE_SERVER, data_storage.get_ed_data_stats(), 'A', ed_node_candidate)
		edge_comp_site = OffloadingSite(8000, 8, 150, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, data_storage.get_ec_data_stats(), 'A', ec_node_candidate)
		edge_reg_site = OffloadingSite(5000, 8, 150, OffloadingSiteCode.EDGE_REGULAR_SERVER, data_storage.get_er_data_stats(), 'A', er_node_candidate)
		cloud_dc_site = OffloadingSite(12000, 128, 1000, OffloadingSiteCode.CLOUD_DATA_CENTER, data_storage.get_cd_data_stats(), 1, cd_node_candidate)
		
		mobile_device = MobileDevice((edge_data_site, edge_comp_site, edge_reg_site), cloud_dc_site)
		
		mobile_device.deploy_network_model()

		if not mixed_mode:
			if application == 'ANTIVIRUS':
				mobile_device.deploy_antivirus_application()

			elif application == 'GPS_NAVIGATOR':
				mobile_device.deploy_gps_navigator_application()

			elif application == 'CHESS':
				mobile_device.deploy_chess_application()

			elif application == 'FACEBOOK':
				mobile_device.deploy_facebook_application()

			elif application == 'FACERECOGNIZER':
				mobile_device.deploy_facerecognizer_application()


		mobile_device.deploy_enhanced_efpo_ode()
		mobile_device.run(number_of_samplings, number_of_app_executions, mixed_mode, sensitivity_analysis)

		mobile_device.deploy_efpo_ode()
		mobile_device.run(number_of_samplings, number_of_app_executions, mixed_mode, sensitivity_analysis)

		mobile_device.deploy_energy_efficient_ode()
		mobile_device.run(number_of_samplings, number_of_app_executions, mixed_mode, sensitivity_analysis)


if __name__ == "__main__":
	main()