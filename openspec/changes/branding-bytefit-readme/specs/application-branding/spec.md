# Spec Delta

## Purpose

Define the product identity shown to users so the login and main application consistently present the academy system as ByteFit.

## ADDED Requirements

### Requirement: The application identifies itself as ByteFit

The application SHALL display the name “ByteFit” as its product identity on the login screen and in the main application navigation.

#### Scenario: View the login screen
- **WHEN** a person opens the login screen
- **THEN** the product name “ByteFit” is visible as the application identity

#### Scenario: View the main application
- **WHEN** an authenticated user views the main application navigation
- **THEN** the product name “ByteFit” is visible as the application identity
