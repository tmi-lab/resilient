import { Component, OnInit } from '@angular/core';
import { RequestsService } from '../../../../services/requests.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-participant-summary',
  templateUrl: './participant-summary.component.html',
  styleUrl: './participant-summary.component.scss'
})
export class ParticipantSummaryComponent implements OnInit{

  participantData: any = {};
  summaryOptions =  [
    {name: 'Scale', code: 'NY', active: true},
    {name: 'Sleepmat', code: 'RM', inactive: true},
    {name: 'Scanwatch', code: 'LDN', inactive: true},
  ];
  selectedOption: any ;
  summaryData: any = {}
  summaryDataColumns: any = [];

  constructor(
    private _requestsService: RequestsService,
    private _router: Router
  ) {}

  ngOnInit(): void {
    this.participantData = history.state;

    console.log(this.participantData);

    this._requestsService.getDevicesByUsername(this.participantData.username).subscribe({
      next: (response) => {
        console.log(response);

      }

    })

  }

  closeParticipantSummary(): void {
    this._router.navigate(['/dashboard/participants']);
  }

  onSummaryOptionClick(): void {
    console.log(this.selectedOption);

  }
}
