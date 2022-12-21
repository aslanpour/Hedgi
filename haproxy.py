#utils file is required for running commands in linux
#sudo apt install haproxy -y
#copy config file to /etc/haproxy/haproxy.cfg
#edit frontend/backend ip, port, mode (tcp or http), etc.
#use this script to customize backends
#Haproxy requires a restart after each reconfiguration, but using haproxyadmin, this is not required. 
import haproxyadmin
from haproxyadmin import haproxy
import utils
utils.shell('touch /run/haproxy/admin.sock')
utils.shell('sudo systemctl restart haproxy.service')
utils.shell('sudo chown ubuntu /run/haproxy/admin.sock')

hap = haproxy.HAProxy(socket_dir='/run/haproxy')

print(hap.show_acl())

print('frontends')
frontends = hap.frontends()
for frontend in frontends:
    print('name={0}, requests={1}, process_nb={2}'.format(frontend.name, frontend.requests, frontend.process_nb))
    # print(frontend.maxconn)
    # frontend.setmaxconn(50000)
    # frontend.status
    # frontend.disable()

def backend_on(server):
    server.setstate(haproxyadmin.STATE_ENABLE)
    server.setstate(haproxyadmin.STATE_READY)
def backend_off(server):
    server.setstate(haproxyadmin.STATE_DISABLE)
    server.setstate(haproxyadmin.STATE_DRAIN)
    server.setstate(haproxyadmin.STATE_MAINT)

# print(hap.info())
print('backends')
backends = hap.backends()
for backend in backends:
    servers = backend.servers()

    # new_server = haproxyadmin.server.Server([haproxyadmin.internal.server._Server(backend, 'ww1', 'eer2')],'backendnodes')
    # servers.append(new_server)
    for server in servers:
        print('***********')
        if server.name == 'w1':
            backend_on(server)
            # server.address = '10.43.249.158'
            server.setweight(50)
        elif server.name == 'w2':
            backend_off(server)
            # server.address = '10.43.249.158'
            server.setweight(50)
        elif server.name == 'w7':
            backend_off(server)
            # server.address = '10.43.111.70'
            server.setweight(50)
        else: 
            backend_off(server)   
    
        # server.port=8080
        # server.address = ''
        # server.setweight(0)
        print('name={0}, requests={1}, weight={2}, address={3}, port={4}, last_status={5}, check_status={6}, requests_per_process={7}, status={8}'.
            format(server.name, server.requests, server.weight, server.address, server.port,server.last_status, server.check_status, server.requests_per_process(), server.status))


#servers accross all backends
# servers = hap.servers()
# for server in servers:
#     server.port=8080
#     # server.address = ''
#     print(server.name, server.requests, server.weight, server.address, server.port,server.last_status, server.requests_per_process(), server.status)
