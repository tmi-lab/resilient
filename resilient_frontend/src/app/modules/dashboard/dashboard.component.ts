import { AfterViewInit, Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements AfterViewInit {

  constructor(
    private _router: Router,
    private _activatedRoute: ActivatedRoute,
    private _messageService: MessageService
  ){}

  ngAfterViewInit(): void {
    this._activatedRoute.queryParams.subscribe({
      next: (params) => {
        this.handleQueryParams(params);
      }
    });
  }

  handleQueryParams(params: any): void {
    console.log(params);

    const paramsAreOk = params.withingsConnected && params.username;
    if (!paramsAreOk) {
      return;
    }

    if (params.withingsConnected === 'true') {
      console.log('true');

      this.showSuccess(params.username);
    } else {
      this.showError(params.username);
    }
  }

  onClickOption(option: string): void {
    this._router.navigate(['/dashboard/' + option]);
  }

  showSuccess(username: string) {
    this._messageService.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Withings connected for ' + username
    });
  }

  showError(username: string) {
    console.log('error');
    this._messageService.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Unable to connect withings for ' + username
    });
  }
}
