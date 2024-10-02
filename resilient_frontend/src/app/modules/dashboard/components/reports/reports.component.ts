import { Component } from '@angular/core';
import { User, Users } from '../../../../shared/models/database-types';


@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss'
})
export class ReportsComponent {

  filteredParticipants: User[] = [];
  participants: User[] = [];
  showDialog: boolean = false;
  username: string;
  usernameFilter: string = '';

  constructor() {
    this.username = '';
  }

  applyUsernameFilter(): void {
    this.filteredParticipants = this.participants.filter(participant => {
      return participant.username.toLowerCase().includes(this.usernameFilter.toLowerCase());
    });
  }

  showCreateReporttModal(): void {
    this.showDialog = true;
    if (this.usernameFilter) {
      this.username = this.usernameFilter
    }
  }

}
