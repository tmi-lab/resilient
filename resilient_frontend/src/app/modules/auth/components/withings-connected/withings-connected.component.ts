import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { LocalStorageService } from '@app/services/local-storage.service';
import { RequestsService } from '@app/services/requests.service';

@Component({
  selector: 'app-withings-connected',
  templateUrl: './withings-connected.component.html',
  styleUrl: './withings-connected.component.scss'
})
export class WithingsConnectedComponent implements OnInit {

  constructor(
    private _router: Router,
    private _localStorageService: LocalStorageService,
    private _requestService: RequestsService,
    private _activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    let failed = true;

    this._activatedRoute.queryParams.subscribe({
      next: (params: any) => {
        failed = this.handleQueryParams(params);
      }
    });

    if (failed) {
      this._router.navigate(['']);
    }
  }

  handleQueryParams(params: any): boolean {
    const paramsAreOk = params.code && params.state;
    if (!paramsAreOk) {
      return true;
    }

    const participantData = this._localStorageService.getData('participant');
    if (!participantData) {
      return true;
    }

    const participantsWithingsData = {
      'username': participantData.username,
      'userId': participantData.id,
      'code': params.code,
      'state': params.state
    };
    let queryParamsData = {};
    this._requestService.saveWithingsCredentials(participantsWithingsData).subscribe({
      next: (response) => {
        queryParamsData = {
          withingsConnected: true,
          username: participantData.username
        }
        const editParticipantData = {
          userId: participantData.id,
          withings_connected: true
        }
        this._requestService.editParticipant(editParticipantData).subscribe({
          next: (response) => {
            console.log("in edit participant", response);

            this.redirectToDashboard(queryParamsData);
          },
          error: (error) => {
            queryParamsData = {
              withingsConnected: false,
              username: participantData.username
            }
            this.redirectToDashboard(queryParamsData);
          }
        });
      },
      error: (error) => {
        queryParamsData = {
          withingsConnected: false,
          username: participantData.username
        }
        this.redirectToDashboard(queryParamsData);
      }
    });
    return false
  }

  redirectToDashboard(queryParamsData: any): void {
    this._localStorageService.clearData('participant');
    this._router.navigate(
      ['dashboard'],
      {
        queryParams: queryParamsData
      }
    );
  }

}
