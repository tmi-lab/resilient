import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  userSignedIn: boolean = false;

  constructor(
    private _router: Router
  ){}

  onClickSignIn(): void {
    this._router.navigate(['auth']);
  }
}
