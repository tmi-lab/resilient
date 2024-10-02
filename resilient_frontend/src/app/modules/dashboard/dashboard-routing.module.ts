import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { ParticipantsComponent } from './components/participants/participants.component';
import { ReportsComponent } from './components/reports/reports.component';
import { DevicesComponent } from './components/devices/devices.component';
import { ParticipantSummaryComponent } from './components/participant-summary/participant-summary.component';

const dashboardRroutes: Routes = [
  {
    path: '',
    //component: DashboardComponent,
    children: [
     { path: '', component: DashboardComponent },
     { path: 'participants', component: ParticipantsComponent },
     { path: 'participant-summary', component: ParticipantSummaryComponent },
     { path: 'reports', component: ReportsComponent },
     { path: 'devices', component: DevicesComponent },
      // { path: 'sign-up', component: SignUpComponent },
      { path: '**', redirectTo: '', pathMatch: 'full' },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(dashboardRroutes)],
  exports: [RouterModule]
})
export class DashboardRoutingModule { }
