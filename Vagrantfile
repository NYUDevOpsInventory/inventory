# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  #config.vm.box = "ubuntu/trusty64"
  config.vm.box = "ubuntu/xenial64"

  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "512"
    vb.cpus = 1
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy the ssh keys into the vm
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  if File.exists?(File.expand_path("~/.ssh/id_rsa.pub"))
    config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/id_rsa.pub"
  end

  # Change the permission of files and directories
  # so that nosetests runs without extra arguments.
  config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=775,fmode=664"]

  ######################################################################
  # Setup a Python development environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    apt-get install -y git python-pip python-dev build-essential
    pip install --upgrade pip
    sudo apt-get -y autoremove

    echo "\n******************************"
    echo " Installing Bluemix CLI"
    echo "******************************\n"
    wget -q -O - https://clis.ng.bluemix.net/download/bluemix-cli/latest/linux64 | tar xzv
    cd Bluemix_CLI/
    ./install_bluemix_cli
    cd ..
    rm -fr Bluemix_CLI/
    bluemix config --usage-stats-collect false

    # Install PhantomJS for Selenium browser support
    echo "\n***********************************"
    echo " Installing PhantomJS for Selenium"
    echo "***********************************\n"
    sudo apt-get install -y chrpath libssl-dev libxft-dev
    # PhantomJS https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    cd ~
    export PHANTOM_JS="phantomjs-1.9.7-linux-x86_64"
    #export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
    wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
    sudo tar xvjf $PHANTOM_JS.tar.bz2
    sudo mv $PHANTOM_JS /usr/local/share
    sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
    rm -f $PHANTOM_JS.tar.bz2
    
    # Install app dependencies
    cd /vagrant
    sudo pip install -r requirements.txt
    # Make vi look nice
    sudo -u ubuntu echo "colorscheme desert" > ~/.vimrc
  SHELL

  ######################################################################
  # Add MySQL docker container
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "Preparing MySQL data share"
    sudo mkdir -p /var/lib/mysql
    sudo chown vagrant:vagrant /var/lib/mysql
  SHELL

  config.vm.provision "docker" do |d|
    d.pull_images "mariadb"
    d.run "mariadb",
      args: "--restart=always -d --name mariadb -p 3306:3306 -v /var/lib/mysql:/var/lib/mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=yes"
  end

  # Create data table after Docker is running
  config.vm.provision "shell", inline: <<-SHELL
    # Wait for mariadb to come up
    echo "Waiting 20 seconds for mariadb to start..."
    sleep 20
    cd /vagrant
    python create_table.py
    cd
  SHELL

end
