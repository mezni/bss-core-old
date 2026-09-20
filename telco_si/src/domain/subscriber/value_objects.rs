use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::error::SubscriberError;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SubscriberStatus {
    Active,
    Suspended,
    Terminated,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct SubscriberId(Uuid);

impl SubscriberId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }

    pub fn value(&self) -> Uuid {
        self.0
    }

    pub fn from_uuid(value: Uuid) -> Self {
        Self(value)
    }
}

impl Default for SubscriberId {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AccountNumber(String);

impl AccountNumber {
    pub fn new(value: impl Into<String>) -> Result<Self, SubscriberError> {
        let value = value.into();

        if value.trim().is_empty() {
            return Err(SubscriberError::InvalidAccountNumber(
                "account number cannot be empty".to_string(),
            ));
        }

        Ok(Self(value))
    }

    pub fn value(&self) -> &str {
        &self.0
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Money {
    cents: i64,
}

impl Money {
    pub fn zero() -> Self {
        Self { cents: 0 }
    }

    pub fn from_cents(cents: i64) -> Result<Self, SubscriberError> {
        if cents < 0 {
            return Err(SubscriberError::NegativeBalance);
        }

        Ok(Self { cents })
    }

    pub fn cents(&self) -> i64 {
        self.cents
    }

    pub fn add(&mut self, amount: Money) {
        self.cents += amount.cents;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn account_number_accepts_valid_value() {
        let account = AccountNumber::new("ACC-10001");

        assert!(account.is_ok());
    }

    #[test]
    fn account_number_rejects_empty_value() {
        let account = AccountNumber::new("");

        assert!(account.is_err());
    }

    #[test]
    fn account_number_rejects_whitespace() {
        let account = AccountNumber::new("   ");

        assert!(account.is_err());
    }

    #[test]
    fn money_starts_at_zero() {
        let money = Money::zero();

        assert_eq!(money.cents(), 0);
    }

    #[test]
    fn money_can_be_created_from_cents() {
        let money = Money::from_cents(2550).unwrap();

        assert_eq!(money.cents(), 2550);
    }
}
