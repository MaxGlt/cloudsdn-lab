Vagrant.configure("2") do |config|
    config.vm.box = "debian/bookworm64"
  
    # Controller : OVS + Ryu
    config.vm.define "controller" do |controller|
      controller.vm.hostname = "controller"
      controller.vm.network "private_network", ip: "192.168.56.10"
      controller.vm.provider "virtualbox" do |vb|
        vb.memory = 1024
        vb.cpus = 1
      end
      controller.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_ryu.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "controller"
      end

      controller.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_node-exporter.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "controller"
      end
    end
  
    # Router 1
    config.vm.define "router1" do |r1|
      r1.vm.hostname = "router1"
      r1.vm.network "private_network", ip: "192.168.56.11"
      r1.vm.network "private_network", ip: "192.168.10.254", virtualbox__intnet: "net-client1"
      r1.vm.provider "virtualbox" do |vb|
        vb.memory = 512
      end
      r1.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_frr.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "router1"
      end

      r1.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_node-exporter.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "router1"
      end
   end
  
    # Router 2
    config.vm.define "router2" do |r2|
      r2.vm.hostname = "router2"
      r2.vm.network "private_network", ip: "192.168.56.12"
      r2.vm.network "private_network", ip: "192.168.20.254", virtualbox__intnet: "net-client2"
      r2.vm.provider "virtualbox" do |vb|
        vb.memory = 512
      end
      r2.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_frr.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "router2"
      end

      r2.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_node-exporter.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "router2"
      end
   end

    # # Monitoring (Grafana + Prometeus)
    # config.vm.define "monitoring" do |monitoring|
    #   monitoring.vm.hostname = "monitoring"
    #   monitoring.vm.network "private_network", ip: "192.168.56.13"
    #   monitoring.vm.provider "virtualbox" do |vb|
    #     vb.memory = 1024
    #   end
    #   monitoring.vm.provision "ansible" do |ansible|
    #     ansible.playbook = "ansible/playbook_monitoring.yml"
    #     ansible.inventory_path = "ansible/inventory.ini"
    #     ansible.limit = "monitoring"
    #   end
    # end

    # Client 1
    config.vm.define "client1" do |client1|
      client1.vm.hostname = "client1"
      client1.vm.network "private_network", ip: "192.168.10.1", virtualbox__intnet: "net-client1"
      client1.vm.provider "virtualbox" do |vb|
        vb.memory = 512
      end
      client1.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_client.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "client1"
      end
    end
    # Client 2
    config.vm.define "client2" do |client2|
      client2.vm.hostname = "client2"
      client2.vm.network "private_network", ip: "192.168.20.1", virtualbox__intnet: "net-client2"
      client2.vm.provider "virtualbox" do |vb|
        vb.memory = 512
      end
      client2.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/playbook_client.yml"
        ansible.inventory_path = "ansible/inventory.ini"
        ansible.limit = "client2"
      end
    end
  end
  