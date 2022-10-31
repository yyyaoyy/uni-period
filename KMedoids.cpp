#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <climits>
#include <cmath>
using namespace std;

struct packet{
	string src_addr;
	string dst_addr;
	int src_port;
	int dst_port;
	int protocol;
	int arrival_time;
	int packet_length;
	bool operator==(packet &p){
		if(src_addr == p.src_addr &&
			dst_addr == p.dst_addr &&
			src_port == p.src_port &&
			dst_port == p.dst_port &&
			protocol == p.protocol)
			return true;
		return false;
	}
};

struct flow{
	struct packet pack;
	int num_pack;
	int total_length;
	int total_transfer_time;
	int last_arrival_time;
};

struct flow_info{
	float avg_transfer_time;
	float avg_packet_length;
};

float **dis;
void dis_init(vector<flow_info> &fs, int n){
	dis = new float*[n];
	for(int i = 0; i < n; i++)
		dis[i] = new float[n];
	for(int i = 0; i < n; i++){
		for(int j = 0; j < n; j++){
			if(i == j){
				dis[i][j] = 0;
			} else{
				dis[i][j] = fabs(fs[i].avg_transfer_time - fs[j].avg_transfer_time) + 
							fabs(fs[i].avg_packet_length - fs[j].avg_packet_length);
			}

		}
	}
}

struct medo_info{
	vector<int> centers;
	vector<int> points;
	vector<int> center_of_points;
	medo_info(int ncenter, int npoint){
		centers.resize(ncenter);
		center_of_points.resize(npoint);
		points.resize(npoint-ncenter);
	}
	void set_point(void){
		for(int i = 0; i < center_of_points.size(); i++)
			center_of_points[i] = -1;
		for(int i = 0; i < centers.size(); i++)
			center_of_points[centers[i]] = centers[i];
		for(int i = 0, j = 0; i < center_of_points.size(); i++){
			if(center_of_points[i] != i)
				points[j++] = i;
		}
	}
	void first_step(){
		for(int i = 0; i < center_of_points.size(); i++){
			if(center_of_points[i] == i)
				continue;
			float min_dis = (float)INT_MAX;
			int center;
			for(int j = 0; j < centers.size(); j++){
				if(min_dis > dis[i][centers[j]]){
					min_dis = dis[i][centers[j]];
					center = centers[j];
				}
			}
			center_of_points[i] = center;
		}
		for(int i = 0, j = 0; i < points.size(); i++)
			if(center_of_points[i] != i)
				points[j++] = i;
	}
};

float medo_cost_diff(medo_info &a, medo_info &b){
	float totala = 0;
	float totalb = 0;
	for(int i = 0; i < a.center_of_points.size(); i++){
		totala += dis[i][a.center_of_points[i]];
		totalb += dis[i][b.center_of_points[i]];
	}
	//printf("%g\t\t%g\n", totala, totalb);
	return totala - totalb;
	/*
	for(int i = 0; i < a.center_of_points.size(); i++){
		total += dis[i][a.center_of_points[i]]
				 - dis[i][b.center_of_points[i]];
	}
	return total;
	*/
}

int str2packet(char *s, packet *p){
	char src_addr[32] = "";
	char dst_addr[32] = "";
	int src_port;
	int dst_port;
	int protocol;
	int arrival_time;
	int length;
	
	if(sscanf(s, "%s %d %s %d %d %d %d", src_addr, &src_port, dst_addr, &dst_port, &protocol, &arrival_time, &length) != 7)
		return -1;
	p->src_addr = string(src_addr);
	p->dst_addr = string(dst_addr);
	p->src_port = src_port;
	p->dst_port = dst_port;
	p->protocol = protocol;
	p->arrival_time = arrival_time;
	p->packet_length = length;

	return 0;
}

void flows2file(vector<flow> &f, FILE *file, vector<flow_info> &fs){
		int idx = 0;
		for(int i = 0; i < f.size(); i++){
				int n = f[i].num_pack;
				struct flow_info flow_info;
				if(n < 2) 
					continue;
				flow_info.avg_transfer_time = 1.0*f[i].total_transfer_time/(n-1);
				flow_info.avg_packet_length = 1.0*f[i].total_length/n;
				fprintf(file, 
					"%d %.2f %.2f\n", 
					idx++, 
					flow_info.avg_transfer_time,
					flow_info.avg_packet_length);
				fs.push_back(flow_info);
		}
}

void medo2file(medo_info &m, FILE *f){
	float total = 0;
	for(int i = 0; i < m.center_of_points.size(); i++)
		total += dis[i][m.center_of_points[i]];
	fprintf(f, "%.2f\n", total);

	for(int i = 0; i < m.centers.size(); i++)
		fprintf(f, "%d ", m.centers[i]);
	fprintf(f, "\n");

	for(int i = 0; i < m.centers.size(); i++){
		for(int j = 0; j < m.center_of_points.size(); j++){
			if(m.center_of_points[j] == m.centers[i])
				fprintf(f, "%d ", j);
		}
		fprintf(f, "\n");
	}
}

void add2flow(packet &pack, vector<flow> &f){

	for(int i = 0; i < f.size(); i++){
		if(pack == f[i].pack){
			f[i].total_length += pack.packet_length;
			f[i].num_pack++;
			f[i].total_transfer_time += pack.arrival_time - f[i].last_arrival_time;
			f[i].last_arrival_time = pack.arrival_time;
			return;
		}
	}

	flow flow;
	flow.pack = pack;
	flow.num_pack = 1;
	flow.total_length = pack.packet_length;
	flow.total_transfer_time = 0;
	flow.last_arrival_time = pack.arrival_time;

	f.push_back(flow);

	return;
}

int load_medos(FILE *f, vector<int> &medos){
	int n, medo;
	fscanf(f, "%d", &n);
	for(int i = 0; i < n; i++){
		fscanf(f, "%d", &medo);
		medos.push_back(medo);
	}
	return n;
}

void vector_print(vector<int> &v)
{
	printf("%ld, ", v.size());
	for(int i = 0; i < v.size(); i++)
		printf("%d ", v[i]);
	putchar('\n');
}

medo_info k_medo(vector<flow_info> &fs, int n, vector<int> medos){

	medo_info kmedo(n, fs.size());
	kmedo.centers = medos;
//printf("kmedo-center: ");
//vector_print(kmedo.centers);

	while(1){
		kmedo.set_point();
		kmedo.first_step();
	//printf("kmedo-center_of_points: ");
	//vector_print(kmedo.center_of_points);
	//printf("kmedo-points: ");
	//vector_print(kmedo.points);
		medo_info tmp = kmedo;
		vector<int> &points = kmedo.points;
		vector<int> new_centers;
		float min_cost = (float)INT_MAX;
		for(int i = 0; i < kmedo.centers.size(); i++)
			for(int j = 0; j < points.size(); j++){
				tmp.centers = kmedo.centers;
				tmp.centers[i] = points[j];
				tmp.set_point();
				tmp.first_step();
				
		/*
		printf("tmp-points: ");
		vector_print(tmp.points);
		printf("%ld: ", points.size());
		vector_print(points);
		printf("i=%d j=%d tmp: ", i, j);
		printf("\t\tkmedo: ");
		vector_print(kmedo.centers);
			
		*/
				float cost = medo_cost_diff(tmp, kmedo);
				if(min_cost > cost){
					min_cost = cost;
					new_centers = tmp.centers;
				}
			}
		//printf("min_cost = %g\n", min_cost);
		if(min_cost >= 0)
			break;
		kmedo.centers = new_centers;
	}
	return kmedo;
}

int main(int argc, char *argv[]){
	
	FILE *pack_file;
	FILE *medo_file;
	FILE *flow_file;
	FILE *kmcl_file;

	vector<flow> flows;
	vector<flow_info> fs;

	if(argc != 3){
		printf("usage: %s %s %s\n", argv[0], "<packet file>", "<medos file>");
		exit(-1);
	}

	pack_file = fopen(argv[1], "r");
	medo_file = fopen(argv[2], "r");
	flow_file = fopen("Flow.txt", "w");
	kmcl_file = fopen("KMedoidsClusters.txt", "w");

	if(pack_file == NULL || medo_file == NULL || flow_file == NULL || kmcl_file == NULL){
		printf("open file error\n");
		exit(-1);
	}

	char line[1024];
	while(!feof(pack_file)){
		packet pack;
		if(fgets(line, sizeof(line), pack_file) == NULL)
			break;
		if(str2packet(line, &pack) == 0)
			add2flow(pack, flows);
	}

	int idx = 0;
	flows2file(flows, flow_file, fs);

	vector<int> medos;
	int n = load_medos(medo_file, medos);
	
	dis_init(fs, fs.size());
	medo_info ret = k_medo(fs, n, medos);

	medo2file(ret, kmcl_file);
	fclose(kmcl_file);
	fclose(pack_file);
	fclose(medo_file);
	fclose(flow_file);

	return 0;
}
