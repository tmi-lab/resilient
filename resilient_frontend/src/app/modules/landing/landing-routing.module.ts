import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { LandingComponent } from './landing.component';

const landingRroutes: Routes = [
  {
    path: '',
    component: LandingComponent
  },
];

@NgModule({
  imports: [RouterModule.forChild(landingRroutes)],
  exports: [RouterModule]
})
export class LandingRoutingModule { }
