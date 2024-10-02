import { Component, OnInit } from '@angular/core';
import { Device, Devices, User, Users } from '../../../../shared/models/database-types';
import { RequestsService } from 'src/app/services/requests.service';
import { ICONS } from '@shared/constants/icons';

@Component({
  selector: 'app-devices',
  templateUrl: './devices.component.html',
  styleUrl: './devices.component.scss'
})
export class DevicesComponent implements OnInit {
  icons = ICONS
  devices: Device[] = [];
  filteredDevices: Device[] = [];
  showDialog: boolean = false;
  username: string;
  usernameFilter: string = '';

  constructor(
    private _requestService: RequestsService
  ) {
    this.username = '';
  }

  ngOnInit(): void {
    this.getDevices();
  }

  getDevices(): void {
    this._requestService.getDevices().subscribe({
      next: (answer: any) => {
        if (answer) {
          console.log(answer);
          this.devices = Object.values(answer.devices);
          this.filteredDevices = this.devices;

        }
      }
    })
  }

  applyUsernameFilter(): void {
    // this.filteredParticipants = this.participants.filter(participant => {
    //   return participant.username.toLowerCase().includes(this.usernameFilter.toLowerCase());
    // });
  }

}
