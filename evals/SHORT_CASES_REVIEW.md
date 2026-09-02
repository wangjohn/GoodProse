# Short review case candidates

Each candidate pairs a window of your authentic draft with the exact published section
it became. Approve the ones whose input is a fair brief for the section (set
`"review_status": "approved"` in the JSONL, editing `input` if needed), reject the rest,
then run `promote-short-cases`. Recall is the share of the section's words found in the
draft window; precision is the share of the window that matched. Low recall means you
wrote most of the section fresh, so the window is a weak brief unless you edit it.

Candidates: 18

## external-database-abstractions-golang--001--short

`candidate` - recall 0.39 - precision 0.66 - window 246 words -> section 420 words - draft paragraphs 1..9

### Input

````text
Turn these notes into one section of a blog post; return only that section.

Blog post: Database abstractions for Golang

At Assembled, we've been using Golang as our exclusive backend language since our founding in 2018. We run a pretty standard web application with a frontend built in React. Early on, we noticed that running a Golang webserver comes with its own particular set of challenges that haven't been easily addressed in the standard library or by community packages. Maybe it's because Golang wasn't originally built as a language to run webservers and to directly access SQL, but we found it hard to access our database in consistent and performant ways.

Here are some abstractions we came up with to make database access in Golang easier.

## Challenge 1: Writing performant, reusable SQL queries

### The problem: Sharing code between getting a single row and getting multiple rows

When we first started writing Postgresql queries, we used what the Golang recommended: writing raw SQL and then running those directly. Let's say you're writing an e-commerce application, then you might have the following method to grab a the information on a particular order:

```
GetOrder() (*Order, error) {
  db.QueryRow("")
}
```

This is great if you only need to grab one order, but what if you want to implement a page where a customer can see all their orders and now you need to add a method to fetch multiple orders? The easiest way to reuse your old code is by grabbing all the order ids that match and then reusing that original method that you wrote for `GetOrder()`.

```
GetOrders() ([]Order, error) {
````

### Reference section

```markdown
At [Assembled](http://assembled.com/), we’ve been using Golang as our exclusive backend language since our founding in 2018. We run a pretty standard web application, but we found that accessing the database comes with its own particular set of challenges that haven’t been fully addressed by the Go standard library or community packages.

In this article, we’ll talk about 3 abstractions we’ve built at Assembled that make database access in Golang easier:

*   An interface to share code between single- and multi-row getters
*   A helper method to ensure you’re always handling errors and closing rows when scanning from the database
*   An interface to share code between transactions and non-transactions

## Challenge 1: Writing performant, reusable SQL queries

### The problem: Sharing code between single and multi-row getters

When we first started writing SQL queries, we dutifully wrote raw SQL like many Golang tutorials told us. But we soon ran into problems with this approach. Let’s say you’re writing an e-commerce application, then you might have the following method to get the information for a particular order:

type Order struct {

 ID string

 ItemID string

 Price int

}
func GetOrder(id string) (*Order, error) {

 var order Order

row := db.QueryRow("SELECT id, item_id, price FROM orders WHERE id = $1;", id)

 err := row.Scan(&order.ID, &order.ItemID, &order.Price)

 if err != nil {

 return nil, err

 }

 return &order, nil

}

This is great if you only need to get one order, but what if you want to implement a page where a customer can see all their orders and now you need to add a method to fetch multiple orders? The easiest way to reuse your old code is by getting all the order ids that match and then reusing that original method that you wrote for `GetOrder()`.

func GetAllOrders() ([]Order, error) {

 rows, err := db.QueryRows("SELECT id FROM orders;")

 if err != nil {

 return nil, err

 }

 defer rows.Close()
var ids []string

 for rows.Next() {

 var id string

 if err := rows.Scan(&id); err != nil {

 return nil, err

 }

 ids = append(ids, id)

 }

var orders []Order

 for _, id := range ids {

 order, err := GetOrder(id)

 if err != nil {

 return nil, err

 }

 orders = append(orders, order)

 }

 return orders, nil

}

The problem with the above is that you’re now making `O(# of orders)`queries. This is expensive and non-performant because:

*   Postgres has to parse and generate a query plan for every query
*   You’ll add the packet roundtrip time from your webserver to the database to every request, which can blow up very quickly if you have lots of requests [0].
```

## external-database-abstractions-golang--002--short

`candidate` - recall 0.61 - precision 0.90 - window 230 words -> section 341 words - draft paragraphs 13..21

### Input

````text
Turn these notes into one section of a blog post; return only that section.

Blog post: Database abstractions for Golang

To solve this problem at Assembled, we introduced a bit of abstraction. The important insight here is to realize that whether you're scanning a single database row or multiple database rows, you should be performing the same operations. You always want to populate the same fields on an `Order` every time you pull one out of the database (doesn't matter if you're fetching one order or multiple). So we created a `Scannable` interface that hides the way in which you're fetching a database row.

```
type Scannable interface {
  Scan(dest ...interface{}) error
}
```

Now, you can pass in either `sql.Row` or `sql.Rows` into a single method and perform the same operation. Here's an example of how you might use the `Scannable` interface to reuse code:

```
var orderAttributes = []string{
  "id",
  "total_price",
  "item"
}

ScanOrder() (*Order, error) {
}

GetOrder() {}

GetOrders() {}
```

Now the total time to run `GetOrders` is just the roundtrip time to your database plus the time it takes to select your matching orders and return them from postgres: `30ms + 100ms = 0.13s` (aka MASSIVE SPEEDUP). In addition to the query speed improvements, you've reduced the number of database queries to a constant number for each `GetOrders` call and significantly decreased database load. Finally, you've also made the code easier to reason about and refactor because there is only a single point of entry when you update an attribute on the `Order` struct.
````

### Reference section

```markdown
### The solution: Create an abstraction for scanning a database row

To solve this problem at Assembled, we introduced an abstraction for scans. The important insight here is to realize that whether you’re scanning a single database row or multiple database rows, you should be performing the same operations. You always want to populate the same fields on an `Order` every time you pull one out of the database (whether you’re fetching one order or multiple). So we created a `Scannable` interface that hides the way in which you’re fetching a database row.

type Scannable interface {

 Scan(dest ...interface{}) error

}
Now, you can pass in either `sql.Row` or `sql.Rows` into a single method and perform the same operation. Here’s an example of how you might use the `Scannable` interface to reuse code:

var orderAttributes = []string{

 "id",

 "item_id",

 "price",

}
func ScanOrder(row Scannable) (*Order, error) {

 var order Order

err := row.Scan(&order.ID, &order.ItemID, &order.Price)

 if err != nil {

 return nil, err

 }

 return &order, nil

}

func GetOrder(id string) (*Order, error) {

 query := fmt.Sprintf("SELECT %s FROM orders WHERE id = $1;",

 strings.Join(orderAttributes, ","))

row := db.QueryRow(query, id)

 return ScanOrder(row)

}

func GetOrders(ids []string) ([]Order, error) {

 query := fmt.Sprintf("SELECT %s FROM orders WHERE id = ANY($1);",

 strings.Join(orderAttributes, ","))

rows, err := db.Query(query, pq.Array(ids))

 if err != nil {

 return nil, err

 }

 defer rows.Close()

var orders []Order

 for rows.Next() {

 order, err := ScanOrder(rows)

 if err != nil {

 return nil, err

 }

 orders = append(orders, *order)

 }

 return orders, nil

}

Now the total time to run `GetOrders` is just a single roundtrip time to your database plus the time it takes to select your matching orders and return them from Postgres. In addition to the query speed improvements, you’ve reduced the number of database queries to a constant number for each `GetOrders` call and significantly decreased database load. Finally, you’ve also made the code easier to reason about and refactor because there is only a single point of entry when you update an attribute on the `Order` struct.
```

## external-database-abstractions-golang--003--short

`candidate` - recall 0.38 - precision 0.70 - window 200 words -> section 371 words - draft paragraphs 27..35

### Input

````text
Turn these notes into one section of a blog post; return only that section.

Blog post: Database abstractions for Golang

And this is one of the hardest problems to debug if you don't know what you're looking for. You have to step through a giant codebase, looking for those places where someone forgot to call `rows.Close()`. Let me tell you -- it's not easy to find these instances.

### The solution: Just don't forget

How did we fix this problem at Assembled? We had weekly trainings to remind everyone to never ever ever forget to call `rows.Close()` and publicly shamed engineers who still forgot.

Just kidding -- we created a better abstraction. Code problems like this can generally be fixed by writing better code, so we came up with a new way of scanning rows.

```
func ScanRows(r sql.Rows, scanFunc func(row Scannable) error) error {
  defer r.Close()

var scanErr error
  for r.Next() {
    err := scanFunc(r)
    if err != nil {
      scanErr = err
      break
    }
  }

if r.Err() != nil {
    return r.Err()
  }
  if scanErr != nil {
    return scanErr
  }
  return nil
}
```

This function actually had a couple of extra convenience pieces too -- previously we ended up writing the same error handling over and over again and in this function, we were able to put all of the error handling logic in a single place.
````

### Reference section

```markdown
## Challenge 2: Remembering to close a set of rows

### The problem: At some point, you’re going to forget to close your rows

> Nothing is certain, except death, taxes, and forgetting to close your rows.
>
>  — Benjamin Franklin (probably)

One of the nasty things about Golang’s SQL driver is the mandatory call to`rows.Close()` after completion which releases your connection back into your pool. Failure to call this method results in increased latency, escalating connection pool sizes, and in the worst-case scenario, outages during holidays when no one is deploying.

Unfortunately, this is one of the hardest problems to debug if you don’t know what you’re looking for. You have to step through a giant codebase, looking for those places where someone forgot to call `rows.Close()`. Let me tell you — it’s not easy to find these instances.

### The solution: A helper method where you can’t forget

How did we fix this problem at Assembled? We had weekly trainings to remind everyone to never ever ever forget to call `defer rows.Close()` and publicly shamed engineers who still forgot.

Just kidding — we created a better abstraction via the `ScanRows` helper method:

type Rows interface {

 Close() error

 Err() error

 Next() bool

 Scan(dest ...interface{}) error

}
func ScanRows(r Rows, scanFunc func(row Scannable) error) error {

 var closeErr error

 defer func() {

 if err := r.Close(); err != nil {

 closeErr = err

 }

 }()

var scanErr error

 for r.Next() {

 err := scanFunc(r)

 if err != nil {

 scanErr = err

 break

 }

 }

 if r.Err() != nil {

 return r.Err()

 }

 if scanErr != nil {

 return scanErr

 }

return closeErr

}

Notice that `ScanRows` will always close the rows after it’s finished with them. The function has an added convenience benefit too: it contains error handling that previously was copy pasted over and over again by every engineer.

Here’s how it would work in our `GetOrders` function:

func GetOrders(ids []string) ([]Order, error) {

 query := fmt.Sprintf("SELECT %s FROM orders WHERE id = ANY($1);",

 strings.Join(orderAttributes, ","))
rows, err := db.Query(query, pq.Array(ids))

 if err != nil {

 return nil, err

 }

var orders []Order

 err := models.ScanRows(rows, func(row Scannable) error) error {

 order, err := ScanOrder(rows)

 if err != nil {

 return err

 }

 orders = append(orders, *order)

 return nil

 })

 if err != nil {

 return nil, err

 }

return orders, nil

}
```

## external-database-abstractions-golang--004--short

`candidate` - recall 0.33 - precision 0.60 - window 229 words -> section 418 words - draft paragraphs 38..46  
Note: weak alignment (recall 0.33); rewrite the input by hand from the draft or reject

### Input

````text
Turn these notes into one section of a blog post; return only that section.

Blog post: Database abstractions for Golang

### The problem: Sharing code between both inside and outside of a transacton

Let's say you just wrote a method to store an `Order` into your database:

```
StoreOrder(ctx context.Context, user User, order Order) (Order, error) {
  ...
}
```

Now let's say there are two ways that you might want to use this method:
  1) You import orders from a third party system into your database
  2) Someone makes a purchase on your site to create an order and you want to store payment information and order information at the same time

In case 1, you don't want to store orders in a transaction (remember the whole thing about long running transactions being bad for database performance) so you can simply use your `StoreOrder` method that you've already written. But in case 2, you do want to store your order in a transaction, so you have to do something like this:

```
StoreOrderTx(ctx context.Context, tx sql.Tx, user User, order Order) (Order, error) {
  ...
}

StoreOrderAndUser() {
  tx := db.Begin()
  StorePaymentTx()
  StoreOrderTx()
  Commit()
}
```

It's really hard to reuse your `StoreOrder` method and you actually end up copy/pasting the majority of the code from your original `StoreOrder` method, but it's not operating on a `sql.Tx` instead of a `sql.DB`. If you change any attribute on the `Order` struct, you'll now have to make sure you remember to update both `StoreOrder` and `StoreOrderTx`.
````

### Reference section

```markdown
## Challenge 3: Reusing queries inside of transactions

### The problem: Sharing SQL between transactions and non-transactions

Let’s say you just wrote a method to store an `Order` into your database:

func StoreOrder(db *sql.DB, order Order) error {

 _, err := db.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }
return nil

}

There are a couple of ways you might want to call this method:

1.   Use `StoreOrder` directly. For example, if you’re syncing orders from Stripe
2.   Use `StoreOrder` in conjunction with other database methods. For example, if someone makes a purchase on your site, you want to store both payment information and order information at the same time

In case 1, you don’t want to store orders in a transaction — long running transactions can be bad for database performance, so you can simply use your `StoreOrder` method that you’ve already written. But in case 2, you do want to store your order in a transaction, so you have to add some additional code. Here’s what it ends up looking like:

func StoreOrder(db *sql.DB, order Order) error {

 _, err := db.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }
return nil

}

func StoreOrderTx(tx sql.Tx, order Order) (*Order, error) {

 _, err := tx.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }

return nil

}

func SyncOrderFromStripe(db *sql.DB, stripeID string) (*Order, error) {

 stripeOrder, err := stripeClient.Get(stripeID)

 if err != nil {

 return err

 }

 order := Order{ItemID: stripeOrder.Items[0].ID, Price: stripeOrder.Amount}

 return StoreOrder(db, order)

}

func StoreOrderAndPayment(db *sql.DB, order Order, payment Payment) (*Order, *Payment, error) {

 tx, err := db.Begin()

 if err != nil {

 return nil, nil, err

 }

storedOrder, err := StoreOrderTx(tx, order)

 if err != nil {

 return nil, nil, err

 }

 storedPayment, err := StorePaymentTx(tx, payment)

 if err != nil {

 return nil, nil, err

 }

err = tx.Commit()

 if err != nil {

 return nil, nil, err

 }

 return storedOrder, storedPayment, nil

}

Notice that you have to basically copy everything inside of `StoreOrder` into `StoreOrderTx` with the only difference being that in the former you run the method on `sql.DB` whereas in the latter you run it on `sql.Tx`.

This is a lot of unfortunate code copying, and if you change any attribute in `Order`, you have to remember to update both `StoreOrder` and `StoreOrderTx`. And let’s face it, at some point someone is going to forget and cause a bug.
```

## external-database-abstractions-golang--005--short

`candidate` - recall 0.12 - precision 0.20 - window 152 words -> section 258 words - draft paragraphs 28..35  
Note: weak alignment (recall 0.12); rewrite the input by hand from the draft or reject

### Input

````text
Turn these notes into one section of a blog post; return only that section.

Blog post: Database abstractions for Golang

### The solution: Just don't forget

How did we fix this problem at Assembled? We had weekly trainings to remind everyone to never ever ever forget to call `rows.Close()` and publicly shamed engineers who still forgot.

Just kidding -- we created a better abstraction. Code problems like this can generally be fixed by writing better code, so we came up with a new way of scanning rows.

```
func ScanRows(r sql.Rows, scanFunc func(row Scannable) error) error {
  defer r.Close()

var scanErr error
  for r.Next() {
    err := scanFunc(r)
    if err != nil {
      scanErr = err
      break
    }
  }

if r.Err() != nil {
    return r.Err()
  }
  if scanErr != nil {
    return scanErr
  }
  return nil
}
```

This function actually had a couple of extra convenience pieces too -- previously we ended up writing the same error handling over and over again and in this function, we were able to put all of the error handling logic in a single place.
````

### Reference section

```markdown
### The solution: Interface for database-like objects and a helper for transactions

Instead of copying code, notice that the `StoreOrder` method doesn’t really care whether it’s operating on `sql.DB` or `sql.Tx`, it just cares that it can write to the database. This is a perfect time to bring in the `Database` abstraction to hide this away:

type Database interface {

 Query(query string, args ...interface{}) (*sql.Rows, error)

 QueryRow(query string, args ...interface{}) *sql.Row

 Exec(query string, args ...interface{}) (sql.Result, error)

}
Now you can delete your `StoreOrderTx` method because both `sql.DB` and `sql.Tx` will implement the `Database` interface, which can greatly simplify your code:

func StoreOrder(db Database, order Order) error {

 _, err := db.Exec("INSERT INTO orders (item_id, price) VALUES ($1, $2)",

 order.ItemID,

 order.Price,

 )

 if err != nil {

 return err

 }
return nil

}

func SyncOrderFromStripe(db *sql.DB, stripeID string) (*Order, error) {

 stripeOrder, err := stripeClient.Get(stripeID)

 if err != nil {

 return err

 }

 order := Order{ItemID: stripeOrder.Items[0].ID, Price: stripeOrder.Amount}

 return StoreOrder(db, order)

}

func StoreOrderAndPayment(db *sql.DB, order Order, payment Payment) (*Order, *Payment, error) {

 tx, err := db.Begin()

 if err != nil {

 return nil, nil, err

 }

storedOrder, err := StoreOrder(tx, order)

 if err != nil {

 return nil, nil, err

 }

 storedPayment, err := StorePayment(tx, payment)

 if err != nil {

 return nil, nil, err

 }

err = tx.Commit()

 if err != nil {

 return nil, nil, err

 }

 return storedOrder, storedPayment, nil

}

The `Database` abstraction allows you to create methods for storing and getting from the database that don’t care whether they’re used in a transaction or not.
```

## external-new-products-team--001--short

`candidate` - recall 0.85 - precision 0.82 - window 432 words -> section 436 words - draft paragraphs 1..8

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: How we Built Assembled's New Products Team

Four months ago, we embarked on a journey to create a new AI-powered product at Assembled. There are a lot of ways to launch a new product at a Series-B company, but we decided to create a “startup within a startup” and put the team through a modified version of YCombinator (YC). We had 3 months of intense building and a demo day at the end. Though we knew these initiatives often don’t pan out, we believed we had a unique edge because:

- **We have quite a few early Assemblers still around:** this was an opportunity to leverage their expertise.
- **I was a YC founder back in the winter of 2014, in addition to founding Assembled in 2018:** I sought to recreate the early startup atmosphere I had experienced.

Inspired by this foundation, we formed the New Products Team to build out a new product that enhanced the efficiency of customer support agents. The team consisted of Cameron Skarritt, Jason Ma, Kaytlin Louton, and myself. Here's how we approached our mission:

### Talk to users

A classic YC mantra says that the two most important tasks at a small startup are to **write code  and talk to users.** We took that to heart, especially the “talk to users” part.

Since we’re building for support teams, we focused really heavily on listening and interacting with support agents and managers. We’ve done many dozens of shadowing sessions where we  watch a support agent work and ask questions. These shadow sessions worked really well to enhance our knowledge of agent workflows, but there’s still a barrier of observability where you’re not actually on the hook to finish out a support ticket and you don’t have to deal with the consequences of your replies.

That’s why we also do support takeovers: our team of 4 takes full responsibility of support for a few days and relieves the Assembled customer support team so they can work on other projects. These sessions really helped hone our thinking of what it’s like to literally be a support agent. By being the backstop for Assembled customers, we started to understand small intricacies about a support agent’s day to day that would be difficult observe passively. It’s hard to fathom how much context switching support agents do until you actually run into a ticket that requires the internal admin dashboard, the metrics dashboard, a help center article, and 3 other tabs open to solve. It’s also hard to understand the cognitive load it takes to write an empathetic reply until you spend 5 minutes rewriting the last paragraph over and over again.
```

### Reference section

```markdown
Four months ago, we embarked on a journey to create a new AI-powered product at [Assembled](https://www.assembled.com/). While there are many ways to launch a new product at a Series-B company, we decided to create a “startup within a startup” and put the team through a modified version of [YCombinator](https://www.ycombinator.com/) (YC). We had 3 months of intense building and a demo day at the end. Though we knew these initiatives don’t always pan out, I wanted to recreate the early startup atmosphere that I had experienced when founding Assembled in 2018 and when I was a [YC founder](https://www.linkedin.com/in/johnjianwang/) back in 2014.

So we formed the New Products Team to build something that enhanced the efficiency of customer support agents. Here’s how we approached our mission:

The New Products Team at work in “the dungeon”. Kaytlin made sure we hung up the “Live, laugh, love” sign.

## Talk to users

A classic YC mantra says that the two most important tasks at a small startup are to [**write code and talk to users**](https://www.ycombinator.com/library/4D-yc-s-essential-startup-advice)**.** We took that to heart, especially the “talk to users” part.

Since we’re building for support teams, we focused really heavily on listening and interacting with support agents and managers. We’ve done many dozens of shadowing sessions where we watch a support agent work. These shadow sessions really enhanced our knowledge of agent workflows, but there’s still a barrier of observability where you’re not actually on the hook to finish out a support ticket and you don’t have to deal with the consequences of your replies.

That’s why we also do support takeovers: our team of 4 takes full responsibility of support for a few days and relieves the Assembled customer support team so they can work on other projects. These sessions really helped hone our thinking of what it’s like to literally be a support agent.

By being the backstop for Assembled customers, we started to understand small intricacies about a support agent’s day to day that would be difficult observe passively. It’s hard to fathom how much context switching support agents do until you actually run into a ticket that requires the internal admin dashboard, the metrics dashboard, a help center article, and 3 other tabs open to solve. It’s also hard to understand the cognitive load it takes to write an empathetic reply until you spend 5 minutes rewriting the last paragraph over and over again.

The team talking to users: we’re very heavy on our usage of hand gestures and phone booths.
```

## external-new-products-team--002--short

`candidate` - recall 0.96 - precision 0.90 - window 357 words -> section 337 words - draft paragraphs 8..12

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: How we Built Assembled's New Products Team

### One room, one team

A core belief we held throughout our time was that everyone on the team would be in person, 5 days a week. We ended up commandeering a conference room for the team and we set up a little pod of desks. We even bought a professional sound system with an amplifier to blast electronic music as we were working [0]. We nicknamed it “the dungeon.”

The dungeon did a few things for us:

- **It made changes in direction easier and faster.** Early in our journey, we were making micro-pivots to our strategy every few hours. One hour, we’d be working on a settings page, and the next hour, we’d realize we didn’t really need that setting to be customer visible, so we’d only make it a backend configuration. We were also making larger pivots to strategy every few days. For example, should we investigate that sales use case that came up in our call? Being in person let us brainstorm and adapt quickly to new information and ideas, especially since our strategy was constantly shifting as we looked to discover who we were building for and how to solve their problems.
- **It helped separate us from the rest of the company.** Everyone on the team had areas of focus and expertise in Assembled’s core product of workforce management. However, we needed time and space to think deeply about our new product, and we would only have that ability by creating focus time for ourselves. Our separate room helped make clear that we were focusing on a new problem and allowed us to set more specific times on when we’d work on Assembled’s core product.
- **Most importantly, it was way more fun.** There’s something magical about working and goofing off late into the night in a small room. It makes you feel really connected to the people you’re working with. Disagreements were addressed more candidly, ideas were shared more freely, and the team grew closer. This connection translated into a more cohesive vision and execution of our goals, making "the dungeon" not just a place, but a symbol of our team's identity and mission.
```

### Reference section

```markdown
## One room, one team

A core belief we held throughout our time was that everyone on the team would be in person, 5 days a week. We ended up commandeering a conference room for the team and we set up a little pod of desks. We even bought a professional sound system with an amplifier to blast electronic music as we were working [0]. We nicknamed it “the dungeon.”

The dungeon did a few things for us:

*   **It made changes in direction easier and faster.** Early in our journey, we were making micro-pivots to our strategy every few hours. One hour, we’d be working on a settings page, and the next hour, we’d realize we didn’t really need that setting to be customer visible, so we’d only make it a backend configuration. We were also making larger pivots to strategy every few days. For example, should we investigate that sales use case that came up in our call? Being in person let us brainstorm and adapt quickly to new information and ideas, especially since our strategy was constantly shifting.
*   **It helped separate us from the rest of the company.** Everyone on the team had expertise in Assembled’s core product of workforce management. However, we needed space to think deeply about our new product, and our separate room helped make clear that we were focusing on a new problem and allowed us to set more specific times on when we’d work on Assembled’s core product.
*   **Most importantly, it was way more fun.** There’s something magical about working and goofing off late into the night in a small room. It makes you feel really connected to the people you’re working with. Disagreements were addressed more candidly, ideas were shared more freely, and the team grew closer. This connection translated into a more cohesive vision and execution of our goals, making “the dungeon” not just a place, but a symbol of our team’s identity and mission.

Jason and Nelson discussing data science techniques. More keyboards mean we can ship faster.
```

## external-new-products-team--003--short

`rejected` - recall 1.00 - precision 1.00 - window 343 words -> section 342 words - draft paragraphs 12..17  
Note: auto-rejected: near-verbatim polish case beyond the cap of 2; approve explicitly to keep

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: How we Built Assembled's New Products Team

### Existential crisis? That’s a feature, not a bug

On the our fourth day working together, I made an announcement to the team: what we were doing wasn’t working. We had started out writing code 12 hours a day based on a cool prototype. This prototype wowed our executives, so we jumped into building a real version. But I realized that we had already broken the first rule of startups: you have to build something people want.

We hadn’t yet validated the problem and we hadn’t spoken to users about what their problems were. So we went back to the drawing board and focused exclusively on booking user interviews. We ended up doing ten user interviews the next week. Happily, three of these turned into sales calls and would eventually be our first three users.

Another existential crisis occurred the week after we had launched to two large teams. During launch week, we saw all of our metrics skyrocket — we were hitting all time highs for number of power users, messages sent, and daily actives. But the week after, usage dropped like a ton of bricks. We sat down as a team and tried to introspect what had gone wrong. We realized that this skyrocketing usage was merely people testing our product, and we still weren’t sticky enough to keep users. We needed to keep adding functionality and value before we could keep these users, so we threw out our plans to make it easier to onboard onto the product, and instead focused exclusively on making the product itself more valuable for existing users.

We continued to have many more existential crises. In fact, if we went a week or two without one, we’d start to get worried and introspect if we were being honest enough with ourselves. These existential crises are a feature of startups though — you only lose your existential angst once you find product market fit and a repeatable business model. By design, we were always questioning whether our product provided sufficient value and always introspecting how to add more value.
```

### Reference section

```markdown
## Existential crisis? That’s a feature, not a bug

On our fourth day working together, I made an announcement to the team: what we were doing wasn’t working. We had started out writing code 12 hours a day based on a cool prototype. This prototype wowed our executives, so we jumped into building a real version. But I realized that we had already broken the first rule of startups: you have to build something people want.

We hadn’t yet validated the problem and we hadn’t spoken to users about what their problems were. So we went back to the drawing board and focused exclusively on booking user interviews. We ended up doing ten user interviews the next week. Happily, three of these turned into sales calls and would eventually be our first three users.

Another existential crisis occurred the week after we had launched to two large teams. During launch week, we saw all of our metrics skyrocket — we were hitting all time highs for number of power users, messages sent, and daily actives. But the week after, usage dropped like a ton of bricks. We sat down as a team and tried to introspect what had gone wrong. We realized that this skyrocketing usage was merely people testing our product, and we still weren’t sticky enough to keep users. We needed to keep adding functionality and value before we could keep these users, so we threw out our plans to make it easier to onboard onto the product, and instead focused exclusively on making the product itself more valuable for existing users.

We continued to have many more existential crises. In fact, if we went a week or two without one, we’d start to get worried and introspect if we were being honest enough with ourselves. These existential crises are a feature of startups though — you only lose your existential angst once you find product market fit and a repeatable business model. By design, we were always questioning whether our product provided sufficient value and always introspecting how to add more value.
```

## learnings-from-the-codex-repo--001--short

`rejected` - recall 1.00 - precision 1.00 - window 336 words -> section 341 words - draft paragraphs 0..5  
Note: auto-rejected: near-verbatim polish case beyond the cap of 2; approve explicitly to keep

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

I've been fascinated recently at what the best practices in the new age of engineering look like. But it's hard to find real data on best practices. For example, X has a ton of "information" about what's happening at the cutting edge, but it's very hard to validate whether any of it is real. Talks suffer from the same problem as an exec at a company can say anything they want or stretch the truth. Are people really not looking at any of their code? Are people productively using billions of tokens every day? It's hard to get ground truth on that.

Because of that, I thought OpenAI's open source [Codex repo](https://github.com/openai/codex) would be an good place to get a bit closer to ground truth:

- OpenAI's internal teams have access to edge of the frontier (it's rumored that Astra is a step change above GPT-5.6-sol for example)
- The Codex repo has been open source since it was launched in 2025, so there's plenty of stuff that has happened in the open.
- OpenAI likely has the best pulse of any company in the world (save a few) on how to build software in the agentic engineering way

So I kicked off an analysis of the repo using a combination of Codex (gpt-5.6-sol) and Claude Code (Fable 5) to try to see what they were doing.

My immediate observation is that Codex has seen a step change increase in PRs per week over the last few months. In May 2025, the Rust implementation had 98 commits from six authors, and one person wrote 89 of them. In the first 25 days of August 2026, it had more than 1,000 commits from 135 authors. This is a big jump, and it's an interesting convergence of a few factors: a) likely a lot of coding agent usage b) aggressive hiring for the team and c) heavy investments in guardrails and automation rules that make it easier for many people and agents to work at the same time.
```

### Reference section

```markdown
I've been fascinated recently at what the best practices in the new age of engineering look like. But it's hard to find real data on best practices. For example, X has a ton of "information" about what's happening at the cutting edge, but it's very hard to validate whether any of it is real. Talks suffer from the same problem as an exec at a company can say anything they want or stretch the truth. Are people really not looking at any of their code? Are people productively using billions of tokens every day? It's hard to get ground truth on that.

Because of that, I thought OpenAI's open source [Codex repo](https://github.com/openai/codex) would be an good place to get a bit closer to ground truth:

- OpenAI's internal teams have access to edge of the frontier (it's rumored that Astra is a step change above GPT-5.6-sol for example)
- The Codex repo has been open source since it was launched in 2025, so there's plenty of stuff that has happened in the open.
- OpenAI likely has the best pulse of any company in the world (save a few) on how to build software in the agentic engineering way

So I kicked off an analysis of the repo using a combination of Codex (gpt-5.6-sol) and Claude Code (Fable 5) to try to see what they were doing.

My immediate observation is that Codex has seen a step change increase in PRs per week over the last few months. In May 2025, the Rust implementation had 98 commits from six authors, and one person wrote 89 of them. In the first 25 days of August 2026, it had more than 1,000 commits from 135 authors. This is a big jump, and it's an interesting convergence of a few factors: a) likely a lot of coding agent usage b) aggressive hiring for the team and c) heavy investments in guardrails and automation rules that make it easier for many people and agents to work at the same time.
```

## learnings-from-the-codex-repo--002--short

`candidate` - recall 0.91 - precision 0.92 - window 274 words -> section 289 words - draft paragraphs 27..33

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

# Graduating from small team / handwritten-ish code to large team with agents

The [public Codex repository](https://github.com/openai/codex) started on April 16, 2025 as a TypeScript CLI. Since then, the repo has changed quite significantly. The initial era of the Codex repo had a small number of authors pushing out everything. For example, Michael Bolin [wrote the original Rust implementation](https://github.com/openai/codex/commit/31d0d7a3059063ef266cab1644aa82f87a866c19) and also 150 of the first 169 Rust commits.

However, over time, this has changed dramatically:

|  | May 2025 | March 2026 | August 2026 |
|---|---:|---:|---:|
| Commits per month | 98 | 791 | 893 |
| Regular author identities with 5+ commits | 2 | 28 | 35 |
| Share written by the busiest author | 91% | 14% | 18% |
| Authors landing changes on the median active day | 1 | 12 | ~18 |
| Rust crates touched on the median active day | 4 | 16 | ~28 |
| Commits carrying exact Codex attribution | 0 | 112 of 791 (14.2%), across 19 authors | Not comparable after the landing process changed |

The volume of changes grew roughly 8x, from 98 commits in May 2025 to 791 in March 2026. By August, the repository was already hitting 900 commits. Commit counts are an imperfect measure of output, especially as development practices change, but the surrounding evidence points to a similar story -- there were more authors were shipping on the same day, across many more parts of the codebase.

Even though coding agents have recently gotten much better, part of the sizeable increase in Codex velocity comes down to sheer team size. OpenAI appears to have put a lot more people on the project (137 members now) and generally been able to keep people working on separate parallel streams of work (most authors seem to be working on separate, parallel crates).
```

### Reference section

```markdown
# Graduating from small team / handwritten-ish code to large team with agents

The [public Codex repository](https://github.com/openai/codex) started on April 16, 2025 as a TypeScript CLI. Since then, the repo has changed quite significantly. The initial era of the Codex repo had a small number of authors pushing out everything. For example, Michael Bolin [wrote the original Rust implementation](https://github.com/openai/codex/commit/31d0d7a3059063ef266cab1644aa82f87a866c19) and also 150 of the first 169 Rust commits.

However, over time, this has changed dramatically:

|  | May 2025 | March 2026 | August 2026 |
|---|---:|---:|---:|
| Commits per month | 98 | 791 | 893 |
| Regular author identities with 5+ commits | 2 | 28 | 35 |
| Share written by the busiest author | 91% | 14% | 18% |
| Authors landing changes on the median active day | 1 | 12 | ~18 |
| Rust crates touched on the median active day | 4 | 16 | ~28 |

The volume of changes grew roughly 8x, from 98 commits in May 2025 to 791 in March 2026. By August, the repository was already hitting 900 commits. Commit counts are an imperfect measure of output, especially as development practices change, but the surrounding evidence points to a similar story -- there were more authors were shipping on the same day, across many more parts of the codebase.

Even though coding agents have recently gotten much better, part of the sizeable increase in Codex velocity comes down to sheer team size. OpenAI appears to have put a lot more people on the project (137 members now) and generally been able to keep people working on separate parallel streams of work (most authors seem to be working on separate, parallel crates).

With that many more people and agents changing the code at the same time, the rules around how they work become much more important.
```

## learnings-from-the-codex-repo--003--short

`candidate` - recall 1.00 - precision 1.00 - window 339 words -> section 391 words - draft paragraphs 5..12  
Note: near-verbatim draft; this is a polish case that tests leaving good prose alone, not voice

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

# Agent guardrails and rules

The first interesting thing is the repo's [`AGENTS.md`](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md) file. The Codex repo takes this fairly seriously: it's clear they've put a lot of thought into and have been aggressive at removing slop and extras (the main file is 322 lines).

There are five rules in particular that I found interesting:

**1. ["Never add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`."](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md#L8-L10)** Some tests check these variables to figure out whether they can safely run nested sandboxing or network behavior. An agent might otherwise see those checks, decide they are getting in the way of a test, and "fix" them. I think it's quite smart to find these types of cheating behaviors that you've seen in test runs and encode them as rules.

**2. ["Do not add tests for values that are statically defined" and "Do not add negative tests for logic that was removed."](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md#L29-L31)** These rules are aimed at tests that make a change look more rigorous without checking any meaningful behavior. Coding agents are very good at generating this kind of plausible-looking test volume, so explicitly telling them what not to test keeps the suite focused on behavior that can actually regress.

**4. ["Features that change the agent logic MUST add an integration test."](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md#L112-L123)** Agent behavior usually comes from the combination of context, tools, model responses, and the turn loop, so a small unit test often can't tell you whether the agent will actually do the right thing. Codex's test harness runs the real agent loop against fake model streams. New tests are also supposed to use [an automatic environment setup](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md#L222-L229) so they keep working when the app-server and exec-server are on different operating systems.

**5. ["Avoid bool or ambiguous `Option` parameters."](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md#L14-L20)** If an API can't be changed, opaque values like `false`, `None`, or a bare number need an exact `/*param_name*/` comment next to them. This is already more specific than what you normally see in an instruction file, but the interesting part is that they didn't leave it as an instruction.
```

### Reference section

```markdown
# Agent guardrails and rules

The first interesting thing is the repo's [`AGENTS.md`](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/AGENTS.md) file. The Codex repo takes this fairly seriously: it's clear they've put a lot of thought into and have been aggressive at removing slop and extras (the main file is 322 lines).

There are five rules in particular that I found interesting:

**1. "Never add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`."** [Some tests check these variables](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/codex-rs/core/tests/suite/compact_resume_fork.rs#L18-L60) to figure out whether they can safely run nested sandboxing or network behavior. An agent might otherwise see those checks, decide they are getting in the way of a test, and "fix" them. I think it's quite smart to find these types of cheating behaviors that you've seen in test runs and encode them as rules.

**2. "Do not add tests for values that are statically defined" and "Do not add negative tests for logic that was removed."** These rules are aimed at tests that make a change look more rigorous without checking any meaningful behavior. Coding agents are very good at generating this kind of plausible-looking test volume, so explicitly telling them what not to test keeps the suite focused on behavior that can actually regress.

**4. "Features that change the agent logic MUST add an integration test."** Agent behavior usually comes from the combination of context, tools, model responses, and the turn loop, so a small unit test often can't tell you whether the agent will actually do the right thing. Codex's [`TestCodexBuilder` test harness](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/codex-rs/core/tests/common/test_codex.rs#L325-L341) runs the real agent loop against fake model streams. New tests are also supposed to use [an automatic environment setup](https://github.com/openai/codex/blob/4fea5234664ebc628b1a5322761cb132eaacc9e2/codex-rs/core/tests/common/test_codex.rs#L485-L499) so they keep working when the app-server and exec-server are on different operating systems.

**5. "Avoid bool or ambiguous `Option` parameters."** If an API can't be changed, opaque values like `false`, `None`, or a bare number need an exact `/*param_name*/` comment next to them. This is already more specific than what you normally see in an instruction file, but the interesting part is that they didn't leave it as an instruction.
```

## learnings-from-the-codex-repo--004--short

`candidate` - recall 0.99 - precision 1.00 - window 311 words -> section 320 words - draft paragraphs 13..21  
Note: near-verbatim draft; this is a polish case that tests leaving good prose alone, not voice

### Input

````text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

The ambiguous argument rule is probably my favorite example of what the team does next. Rust makes it easy to end up with calls like this:

```rust
foo(false, None, 1000)
```

It is basically impossible to review that without jumping to the function definition. The Codex team would prefer that you change the API, but when that is impractical they require comments next to ambiguous literal arguments:

```rust
foo(
    /*enabled*/ false,
    /*parent_turn_id*/ None,
    /*timeout_ms*/ 1000,
)
```

They then built a [custom lint](https://github.com/openai/codex/commit/4b31848f5bd112816eb0f7f4e9a33dc2330ea617) that checks whether the comment exactly matches the parameter name in the function definition. It was introduced in March 2026, applied across the Rust workspace a couple of days later, and then moved into Bazel CI.

The other thing worth saying is that these rules did not appear all at once. Support for `AGENTS.md` landed in May 2025. More detailed test guidance followed that summer. Snapshot requirements came in February 2026, the warning about `codex-core` in March, the trait guidance in April, and the model context and change-size rules in June. It looks a lot like the team is taking repeated review feedback and putting it somewhere that the next person or agent will see before making the same mistake.

You can see a rough pattern here: a problem first shows up repeatedly in code review, it gets written into `AGENTS.md` so humans and agents see it before making a change, and then the team turns it into a lint or CI check once the rule is stable enough. Not every rule makes it to the last step, but the expensive and objectively checkable ones tend to.

Codex has 38 lint rules, and I think it's part of what makes the repo easier to work on as an agent because it has a large number of automated checks that prevent out-of policy behavior (and in a deterministic way).
````

### Reference section

````markdown
# Lint rules

The ambiguous argument rule is probably my favorite example of what the team does next. Rust makes it easy to end up with calls like this:

```rust
foo(false, None, 1000)
```

It is basically impossible to review that without jumping to the function definition. The Codex team would prefer that you change the API, but when that is impractical they require comments next to ambiguous literal arguments:

```rust
foo(
    /*enabled*/ false,
    /*parent_turn_id*/ None,
    /*timeout_ms*/ 1000,
)
```

They then built a [custom lint](https://github.com/openai/codex/commit/4b31848f5bd112816eb0f7f4e9a33dc2330ea617) that checks whether the comment exactly matches the parameter name in the function definition. It was introduced in March 2026, applied across the Rust workspace a couple of days later, and then moved into Bazel CI.

The other thing worth saying is that these rules did not appear all at once. Support for `AGENTS.md` landed in May 2025. More detailed test guidance followed that summer. Snapshot requirements came in February 2026, the warning about `codex-core` in March, the trait guidance in April, and the model context and change-size rules in June. It looks a lot like the team is taking repeated review feedback and putting it somewhere that the next person or agent will see before making the same mistake.

You can see a rough pattern here: a problem first shows up repeatedly in code review, it gets written into `AGENTS.md` so humans and agents see it before making a change, and then the team turns it into a lint or CI check once the rule is stable enough. Not every rule makes it to the last step, but the expensive and objectively checkable ones tend to.

Codex has 38 lint rules, and I think it's part of what makes the repo easier to work on as an agent because it has a large number of automated checks that prevent out-of policy behavior (and in a deterministic way).
````

## learnings-from-the-codex-repo--005--short

`rejected` - recall 1.00 - precision 1.00 - window 391 words -> section 391 words - draft paragraphs 21..27  
Note: auto-rejected: near-verbatim polish case beyond the cap of 2; approve explicitly to keep

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

# Investing in an integration test harness

One other thing that I thought was interesting was how much the Codex team has invested in their tests. Tests compose about 615k lines (or 40%) of the codebase, and Codex has also invested in a full mock test harness: they've spent around 7k lines of code across 300+ commits to built out a harness that can stub out http responses from the Responses API. This integration test harness will run a real Codex thread, and it can call tools, apply approvals, and generally iterate on requests as if it's getting responses back from the LLM. It's a really interesting and deterministic way to test a large amount of behavior, and I think it's quite smart to have invested so heavily in this because the Codex loop is ultimately the most important part of the product.

Another area that I was curious about (especially because our team has seen our test suites slow down as our coding agents get better and faster at writing tests), is how they're still able to keep up speed of development despite a large number of tests. Codex doesn't run the same enormous test suite at every stage. While someone is working on a change, the setup is to test only the affected Rust crate. If you change the terminal UI, for example, you run the terminal UI tests, not the entire workspace. This keeps the everyday edit-test loop reasonably fast.

Before a change is merged, CI broadens the coverage. Bazel runs the compatible Rust tests across macOS, Linux, and Windows, while separate jobs check the SDKs, formatting, dependencies, and repository rules. The largest workloads are divided across machines and reuse remote build caches.

After the code reaches main, Codex pays for a much more exhaustive pass. It runs the full Cargo test suite across five platform and architecture combinations. Each platform compiles the tests once, packages the resulting binaries, and distributes their execution across four machines. Slower native Windows checks, release builds, and remote-environment tests also happen here.

Basically, Codex has set up their environment so only relevant tests are run while developing, and get progressively more thorough as a piece of code gets closer to deployment. This makes it so you can still have fast deploys and ship quickly, while keeping safety and correctness in the long run.
```

### Reference section

```markdown
# Investing in an integration test harness

One other thing that I thought was interesting was how much the Codex team has invested in their tests. Tests compose about 615k lines (or 40%) of the codebase, and Codex has also invested in a full mock test harness: they've spent around 7k lines of code across 300+ commits to built out a harness that can stub out http responses from the Responses API. This integration test harness will run a real Codex thread, and it can call tools, apply approvals, and generally iterate on requests as if it's getting responses back from the LLM. It's a really interesting and deterministic way to test a large amount of behavior, and I think it's quite smart to have invested so heavily in this because the Codex loop is ultimately the most important part of the product.

Another area that I was curious about (especially because our team has seen our test suites slow down as our coding agents get better and faster at writing tests), is how they're still able to keep up speed of development despite a large number of tests. Codex doesn't run the same enormous test suite at every stage. While someone is working on a change, the setup is to test only the affected Rust crate. If you change the terminal UI, for example, you run the terminal UI tests, not the entire workspace. This keeps the everyday edit-test loop reasonably fast.

Before a change is merged, CI broadens the coverage. Bazel runs the compatible Rust tests across macOS, Linux, and Windows, while separate jobs check the SDKs, formatting, dependencies, and repository rules. The largest workloads are divided across machines and reuse remote build caches.

After the code reaches main, Codex pays for a much more exhaustive pass. It runs the full Cargo test suite across five platform and architecture combinations. Each platform compiles the tests once, packages the resulting binaries, and distributes their execution across four machines. Slower native Windows checks, release builds, and remote-environment tests also happen here.

Basically, Codex has set up their environment so only relevant tests are run while developing, and get progressively more thorough as a piece of code gets closer to deployment. This makes it so you can still have fast deploys and ship quickly, while keeping safety and correctness in the long run.
```

## learnings-from-the-codex-repo--006--short

`rejected` - recall 1.00 - precision 1.00 - window 207 words -> section 235 words - draft paragraphs 33..37  
Note: auto-rejected: near-verbatim polish case beyond the cap of 2; approve explicitly to keep

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

# Migrations with linting and feature flags

The other fascinating thing we observed in Codex's codebase is some good old-fashioned, high-quality engineering. Their engineering team uses a combination of feature flags, linters, and other rollout mechanisms to ensure safety but also speedin rollout. Large changes are staged so the old and new implementations can coexist, and the migration plan is eventually encoded in lint rules instead of depending on everyone remembering it.

The TUI migration is a nice example. On March 16, the team created a [temporary parallel implementation](https://github.com/openai/codex/commit/db89b73a9cd553ac2a2afda93c9f9bdcc223540c) behind a `tui_app_server` feature flag. Ten days later, they [enabled it by default](https://github.com/openai/codex/commit/e7139e14a29de0411a61658a0e5765e2502a0cd2). Once it was stable, they [deleted the old TUI and retired the feature flag](https://github.com/openai/codex/commit/d65deec61718f291cba5a51de9489603865779df), while continuing to accept the old flag in configuration so existing users would not get an error.

Two weeks later, they added a [CI rule preventing the TUI from importing `codex-core` directly](https://github.com/openai/codex/commit/66e13efd9cfd0dd3525713c8cf27ea7fbcb6b3e4). I think this is a particularly good way to finish a migration. It's easy to clean up a dependency once, but on a team this large, someone will eventually add it back unless CI stops them. The feature flag made it easier to move over incrementally, and the lint rule made sure the team couldn't accidentally undo the work later.
```

### Reference section

```markdown
# Migrations with linting and feature flags

The other fascinating thing we observed in Codex's codebase is some good old-fashioned, high-quality engineering. Their engineering team uses a combination of feature flags, linters, and other rollout mechanisms to ensure safety but also speedin rollout. Large changes are staged so the old and new implementations can coexist, and the migration plan is eventually encoded in lint rules instead of depending on everyone remembering it.

The TUI migration is a nice example. On March 16, the team created a [temporary parallel implementation](https://github.com/openai/codex/commit/db89b73a9cd553ac2a2afda93c9f9bdcc223540c) behind a `tui_app_server` feature flag. Ten days later, they [enabled it by default](https://github.com/openai/codex/commit/e7139e14a29de0411a61658a0e5765e2502a0cd2). Once it was stable, they [deleted the old TUI and retired the feature flag](https://github.com/openai/codex/commit/d65deec61718f291cba5a51de9489603865779df), while continuing to accept the old flag in configuration so existing users would not get an error.

Two weeks later, they added a [CI rule preventing the TUI from importing `codex-core` directly](https://github.com/openai/codex/commit/66e13efd9cfd0dd3525713c8cf27ea7fbcb6b3e4). I think this is a particularly good way to finish a migration. It's easy to clean up a dependency once, but on a team this large, someone will eventually add it back unless CI stops them. The feature flag made it easier to move over incrementally, and the lint rule made sure the team couldn't accidentally undo the work later.
```

## learnings-from-the-codex-repo--007--short

`candidate` - recall 0.91 - precision 0.64 - window 247 words -> section 175 words - draft paragraphs 37..41

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Learnings from the Codex repo

# Conclusion: speed == testing, boundaries, lint, hiring

The Codex team is running and building upon a highly used, production-level codebase while moving incredibly quickly. They've ramped up velocity considerably in the last few months through a combination of AI coding agent usage as well as hiring for new team members. There are a lot more people working on Codex than there were a year ago and many of those people appear to be very effective engineers. The rules around model context, sandbox ownership, backward compatibility, and storage migrations reflect a lot of accumulated experience. This is the same reason I think it is misleading to frame engineering as speed versus quality. People who are good at building software tend to be both faster and better because they know which details matter and which ones don't.

Also, the codebase is explicitly organized to give agents context. They have invested in the tests and boundaries that let all of those people and agents work at the same time. Agent behavior is tested against fake model streams, so tests can run the full model and tool loop without paying for inference or relying on a live model.

The interesting thing is that at least for the Codex team, as implementation got cheaper, it did not make the rest of engineering less important. Codex put a lot of work into a well-designed system, particularly focused on the classic parts of engineering excellence: testing, high quality boundaries and abstractions, automatic linting systems, and
```

### Reference section

```markdown
# Conclusion: speed == testing, boundaries, lint, hiring

The Codex team is running and building upon a highly used, production-level codebase while moving incredibly quickly. They've ramped up velocity considerably in the last few months through a combination of AI coding agent usage as well as hiring for new team members. There are a lot more people working on Codex than there were a year ago and many of those people appear to be very effective engineers. Also, the codebase is explicitly organized to give agents context. OpenAI have invested in the tests and boundaries that let all of those people and agents work at the same time.

The interesting thing is that at least for the Codex team, as implementation got cheaper, it did not make the rest of engineering less important. Codex put a lot of work into a well-designed system, particularly focused on the classic parts of engineering excellence: testing, high quality boundaries and abstractions, automatic linting systems, and of course hiring good people. All of those things seemed to have gotten more important.
```

## why-we-built-143--001--short

`candidate` - recall 0.06 - precision 0.17 - window 65 words -> section 205 words - draft paragraphs 4..5  
Note: author-edited input (aligned window had recall 0.06, precision 0.17)

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Why we built 143

Opening section, before we get into what we built:

At Assembled, we wanted a way to improve our ability to take advantage of coding agents. For a long time even into 2026, we hadn’t been seeing significant increases in velocity from coding agent adoption, and that was frustrating. It seemed like people with completely new repos (individual vibe coders and ai native startups) were reaping huge rewards, but people with production ready, complex systems like ourselves weren’t getting the same levels of change. We felt a lot of FOMO and were trying to figure out what we were doing wrong. After talking to many other teams, We realized we needed to put a lot of effort into shared systems.

- vibe coding isn’t the right word: you want productionalized coding. No one cares about one off apps, everyone cares about making professional coders who are focused on a key problem work faster and more efficiently, while also enabling domain experts who might not have the coding skills to be able to have a clearer way to build for themselves in production.
- The current set of tools helps with the first one, but makes the second part hard. What’s more, the current set of tools largely aren’t focused on how to make teams more productive: they’re focused on individual engineers.
- And why would they be, they’re built by engineers. But as our time running engineering teams, we noticed a bunch of primitives at the wrong level:
```

### Reference section

```markdown
The best person to understand a problem really deeply usually isn't an engineer, it's usually someone who's using the product day in and day out with customers. Or it's the customer support person who sees questions all day about why a particular feature isn't working. While engineers have historically been the only people who could fix things, that's not true anymore.

Now with coding agents, non-engineers can fix things too and tend to be closer to the problems that users run into on a daily basis. The problem is that the tools built on top of these agents weren't made for that person, they were built for engineers by engineers. That's why we built [143](https://143.dev).

# Where it started

At Assembled, we saw this firsthand: our support and product teams kept surfacing fixes that engineers never had time for. Coding agents could have handled many of them, if the tooling didn't assume you lived in a terminal.

143 is the internal coding agent infrastructure we built at [Assembled](https://www.assembled.com) to help our non-engineers with this problem (while also helping our engineers build better software). We wanted coding agents to help with real product work, not just demos and internal tools.
```

## why-we-built-143--002--short

`candidate` - recall 0.16 - precision 0.39 - window 96 words -> section 227 words - draft paragraphs 2..3  
Note: author-edited input (aligned window had recall 0.16, precision 0.39)

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Why we built 143

Section on what we built:

So we started by creating a tiger team to improve our shared infrastructure (enhancing agents.md, investing in ci/cd, building out agent hooks, etc). Eventually, we ran into the fact that we needed to build some system to collect all these things together that was at a team level, not an individual engineer level. We were inspired by stripe minions, ramp inspect, but their systems were internal and not available to the public. So we went and built 143.dev. But we intentionally wanted to build something open source that everyone can take advantage of.

- Automations should be built with team visibility, not for individual engineers. When you’ve got agents running every day to improve your test coverage, identify security vulnerabilities, etc: you want a group of people to be able to monitor those similar to how you handle on call rotations.
- Any intelligence: You should be able to swap out intelligence and coding agents easily. There’s a ton of great coding agents out there. You should be able to use whatever you’d like and switch between them seamlessly. Both agent harnesses and llms themselves are increasingly rapidly, so you want to be able to use whatever is the latest and greatest at any given time without switching out your workflow.
- Usage should be tracked easily across all your users, and ideally not at the token level. You generally want to be able to slice and dice LLM token usage across PRs, linear issues, automations, etc. so that you have a thorough understanding of how each person is using AI and what your top people are doing.
- Hooks that run things on demand. A central concept of programming is event driven architecture and it should be easy for you to run a coding agent or llm when something happens (e.g. someone opens a pull request, when a sentry error appears, when a linear issue gets added, etc.). These should happen automatically without an engineer needing to do something.
- Set up a great environment once for everyone. If you’re working with a team, you don’t want or need everyone to set up their own connections to MCP servers, logging systems, etc. You should set it up once across your entire team, and have everyone leverage the tools that you have set up.
```

### Reference section

```markdown
# What we built

We started with a small tiger team that cleaned up our instructions, invested more in CI/CD, built agent hooks, and made the agent environment less fragile. All of that helped, but it also made the bigger issue obvious: we needed a system that made this work shared across the team as opposed to being trapped inside each engineer's terminal.

We were inspired by internal systems like Stripe Minions and Ramp Inspect, but those were never available to the public. We wanted something open source that other teams could use, adapt, and improve.

We built 143 so the person who spots the bug doesn't need to become an engineer to fix it. That meant:

- **Automations shouldn't be hidden on one engineer's laptop**, so anyone on the team can see what's running and what changed.
- **Teams should be able to swap out intelligence and harnesses** as coding agents and models improve.
- **Shared context should make it natural to start work automatically** from Sentry issues, Linear assignments, PR comments, or scheduled checks.
- **Code review should be handled by agents** on some or all PRs, and they should be able to auto-approve low-risk changes against thresholds you define.
- **You should be able to set up a great environment once for everyone**, with the same repos, credentials, tools, logs, docs, and product context available to the whole team.
```

## why-we-built-143--003--short

`candidate` - recall 0.42 - precision 0.37 - window 203 words -> section 184 words - draft paragraphs 3..4  
Note: author-edited input (aligned window had recall 0.42, precision 0.37)

### Input

```text
Turn these notes into one section of a blog post; return only that section.

Blog post: Why we built 143

Section on why it's open source:

But we intentionally wanted to build something open source that everyone can take advantage of.

Why? Well I owe my career to my early open source work on Ruby on Rails. That’s where I learned about great software fundamentals from people like tenderlove, Santiago pastorino, Jose Valim, Jeremy doerr. Their PR reviews, welcoming attitude, and design pairing was really what I think open source (and software engineering more broadly) is all about. I was just a college stufent, but the rails core team didn’t care who you were: they welcomed contributors from anywhere as long as the PR was good and well intentioned. And they built something that was used by millions of people for the love of the game. This initial early work in open source is what helped me hone my skills. I started by writing tests and little tiny refactors, and I gradually learned more about the rails codebase and started fixing activerecord bugs. The experience was what got me my job at Stripe as one of the first 100 employees (stripe was a big ruby shop), and was the launching pad for the rest of my career. So needless to say, I want this software to be available to the world and hopefully help others, just like how Ruby on Rails changed my life.
```

### Reference section

```markdown
# Open source for everyone

The same idea that you shouldn't have to be an insider to contribute is why we open-sourced 143.

I owe a lot of my career to early open-source work on Ruby on Rails. That is where I learned software fundamentals from people like Aaron Patterson, Santiago Pastorino, Jose Valim, and Jeremy Doerr. Their PR reviews, their patience, and their willingness to design-pair with strangers on the internet shaped how I think about software.

I was just a college student, but the Rails core team didn't care who I was. If a PR was good and well-intentioned, it was welcome. I started with tests and tiny refactors, learned more of the codebase, and eventually got really deep into the internals of Active Record. That work helped me get my job at Stripe and became the launching pad for the rest of my career.

I want 143 to be available in that same spirit. I hope it helps other people and teams the way open source helped me. The code is [on GitHub](https://github.com/assembledhq/143) under an MIT License.
```
