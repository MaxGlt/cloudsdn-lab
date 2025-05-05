Vagrant.configure("2") do |config|

  # VM1: Switch SDN avec Open vSwitch et contrôleur Ryu
  config.vm.define "sdn" do |sdn|
      sdn.vm.box = "debian/bullseye64"
      sdn.vm.hostname = "sdn"
      sdn.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
          vb.cpus   = 1
      end
      sdn.vm.provision "shell", path: "provision/sdn/sdn.sh"
  end

  # VM2: Routeur 1 : Routage dynamique via FRRouting 
  config.vm.define "r1" do |r1|
      r1.vm.box = "debian/bullseye64"
      r1.vm.hostname = "r1"
      r1.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
          vb.cpus   = 1
      end
      r1.vm.provision "shell", path: "../provision/routing/r1.sh"
  end

  # VM3: Routeur 2 : Routage dynamique via FRRouting 
  config.vm.define "r2" do |r2|
      r2.vm.box = "debian/bullseye64"
      r2.vm.hostname = "r2"
      r2.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
          vb.cpus   = 1
      end
      r2.vm.provision "shell", path: "../provision/routing/r2.sh"
  end

  # VM4: Monitoring : Monitoring avec Prometheus + Grafana
  config.vm.define "monitoring" do |monitoring|
      monitoring.vm.box = "debian/bullseye64"
      monitoring.vm.hostname = "monitoring"
      monitoring.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
          vb.cpus   = 1
      end
      monitoring.vm.provision "shell", path: "../provision/monitoring/monitoring.sh"
  end

  # VM5: Client 1 : hôte client Linux
  config.vm.define "client1" do |client1|
      client1.vm.box = "debian/bullseye64"
      client1.vm.hostname = "client1"
      client1.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
          vb.cpus   = 1
      end
      client1.vm.provision "shell", path: "../provision/clients/client1.sh"
  end

  # VM6: Client 2 : hôte client Linux
  config.vm.define "client2" do |client2|
      client2.vm.box = "debian/bullseye64"
      client2.vm.hostname = "client2"
      client2.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
          vb.cpus   = 1
      end
      client2.vm.provision "shell", path: "../provision/clients/client2.sh"
  end
end