import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
describe('application navigation',()=>{it('renders overview shell',()=>{render(<BrowserRouter><App/></BrowserRouter>);expect(screen.getByText('RETAIL CUSTOMER INTELLIGENCE')).toBeTruthy();});});
