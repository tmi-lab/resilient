import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WithingsConnectedComponent } from './withings-connected.component';

describe('WithingsConnectedComponent', () => {
  let component: WithingsConnectedComponent;
  let fixture: ComponentFixture<WithingsConnectedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [WithingsConnectedComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(WithingsConnectedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
