import dotenv from 'dotenv'; 
dotenv.config()
import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano, contractAddress, beginCell, internal, fromNano, SendMode, Address, Contract, OpenedContract } from '@ton/core';
import { content } from '../scripts/deployMaster';
import { TokenMaster } from "../build/TokenMaster/tact_TokenMaster"
import { JobOffer, storeDeploy, storeDeployOk, storeMint, storeRevoke, storeWithdraw, storeApprove, storeGetJob, storeCompleteJob, storeConfirmJob } from "../build/TokenMaster/tact_JobOffer"
import { TokenWallet } from "../build/TokenMaster/tact_TokenWallet"
import '@ton/test-utils';
import { assert, log } from 'console';
import { deploy, mint } from './test_utils';


const title = "Sell Store 321"
const description = "Selling1 a bike in excellent condition! Trek brand, 2022 model. Lightweight aluminum frame, disc brakes, 21 speeds. Ideal for city trips and long walks. Includes: headlights, bell, running board. Price 25,000 rub. Negotiable. Call: +7-999-123-45-67." 
const price = toNano(100)
const order = "Sell store 2"

const deployAmount = toNano("0.65")
const TransferAmount = toNano("0.65")
const simple_transfer_amount = toNano("0.2")


describe('JobOffer', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let poster: SandboxContract<TreasuryContract>;
    let doer: SandboxContract<TreasuryContract>;
    let third_user: SandboxContract<TreasuryContract>;
    let platform: SandboxContract<TreasuryContract>;
    let master: SandboxContract<TokenMaster>;
    let posterJW: SandboxContract<TokenWallet>;
    let deployerJW: SandboxContract<TokenWallet>;
    let doerJW: SandboxContract<TokenWallet>;
    let JOJW: SandboxContract<TokenWallet>;

    const JettonDecimal = 9
    let jobOffer: SandboxContract<JobOffer>;

    let DeployOffer: any
    
    beforeEach(async () => {
        blockchain = await Blockchain.create();
        deployer = await blockchain.treasury('deployer'); //EQBGhqLAZseEqRXz4ByFPTGV7SVMlI4hrbs-Sps_Xzx01x8G
        poster = await blockchain.treasury('poster'); //EQD-N3h6Wk-IEIVhXtz--H9qc5Nyk5M2VsTTavuytejk8d0X
        doer = await blockchain.treasury('doer'); //EQB1cX3AWEUC64v6rhRjwdEk0fRV6Qn-JBFqXSFY30PitP6c
        platform = await blockchain.treasury('platform'); 
        third_user = await blockchain.treasury('third_user'); //EQD6BRvNYA5F5U4g8YJ9utWbtxQQDoVhjemWlUBaK3eAKBDL

        // Jetton Master
        let master_init = await TokenMaster.init(
            deployer.address, content
        )
        master = blockchain.openContract(await TokenMaster.fromInit(
            deployer.address, content
        ));

        await deployer.send(
            {
                value: deployAmount,
                to: master.address,
                body: beginCell().store(
                    storeDeploy(
                        {
                            $$type: "Deploy",
                            queryId: 2n
                        }
                    )
                ).endCell(),
                init: {
                    code: master_init.code,
                    data: master_init.data
                }
            }
        )

        deployerJW = blockchain.openContract(await TokenWallet.fromInit(
            deployer.address, master.address
        ))

        posterJW = blockchain.openContract(await TokenWallet.fromInit(
            poster.address, master.address
        ))

        doerJW = blockchain.openContract(await TokenWallet.fromInit(
            poster.address, master.address
        )) // address EQDQnV1fm26m2w4l1GImLSGTZQ-XmpqooRb4adlcLbfIyjdz
        log(doerJW.address, "DOERJW ADDRESS")


        // JOB OFFER CREATION
        jobOffer = blockchain.openContract(await JobOffer.fromInit(
            title, description, price, order, master.address
        ))
        let JOJW_address = await master.getGetWalletAddress(jobOffer.address)
        JOJW = blockchain.openContract(
            TokenWallet.fromAddress(
                JOJW_address, 
            )
        )
        // DEPLOY
        DeployOffer = async () => {
            await poster.send(
                {
                    value: toNano(1),
                    to: jobOffer.address,
                    body: beginCell().store(
                        storeDeploy({
                            $$type: "Deploy",
                            queryId: 1n
                        })
                    ).endCell(),
                    init: {code: jobOffer.init?.code,
                        data: jobOffer.init?.data
                    }
                }
            )
            let dep_res = await jobOffer.getJobData()
            expect(JOJW.address).toEqualAddress(dep_res.my_jetton_address)
            expect(master.address).toEqualAddress(dep_res.jetton_master)
        }
        
    });

    it("Test: should recieve jettons to Wallet", async () => {
        await DeployOffer()
        let mint_amount = price
        await mint(deployer, master, jobOffer.address, mint_amount)
        let res = await JOJW.getGetWalletData()
        expect(res.balance).toBeGreaterThanOrEqual(mint_amount)
    });

    it("Test: should revoke", async () => {
        await DeployOffer()
        let mint_amount = price
        await mint(deployer, master, jobOffer.address, mint_amount)
        let s = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        expect(s.transactions).toHaveTransaction({
            from: poster.address,
            to: jobOffer.address,
            success: true,
            endStatus: 'non-existing',
            destroyed: true
        });
    });

    it("Test: should not revoke(not poster)", async () => {
        await DeployOffer()
        let mint_amount = price
        await mint(deployer, master, jobOffer.address, mint_amount)
        let s = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        let res = await JOJW.getGetWalletData()
        expect(s.transactions).toHaveTransaction({
            from:doer.address,
            to: jobOffer.address,
            success: false,
            op: 0x011f
        })
        expect(res.balance).toEqual(mint_amount)
    });

    it("Test: Approve then Revoke", async () => {
        await DeployOffer()
        let mint_amount = price
        await mint(deployer, master, jobOffer.address, mint_amount)
        // Case Fail because of not Tracking address
        let s = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeApprove({
                        $$type: "Approve",
                        amount: mint_amount,
                    })
                ).endCell()
            }
        )
        expect(s.transactions).toHaveTransaction({
            from:doer.address,
            to: jobOffer.address,
            success: false,
            op: 0x013f
        })

        // Real approve
        let w = await platform.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeApprove({
                        $$type: "Approve",
                        amount: mint_amount,
                    })
                ).endCell()
            }
        )
        expect(w.transactions).toHaveTransaction({
            from:platform.address,
            to: jobOffer.address,
            success: true,
            op: 0x013f,
            outMessagesCount: 1 // notification 
        })
        // Note: Total fees 3978328n

        let JOstateCheck = await jobOffer.getJobData()
        expect(JOstateCheck.state).toEqual(1n) // Offer published

        // Revoke after this 
        let rev_res = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeRevoke({
                        $$type: "Revoke",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        expect(rev_res.transactions).toHaveTransaction({
            from: poster.address,
            to: jobOffer.address,
            success: true,
            endStatus: 'non-existing',
            destroyed: true,
            outMessagesCount: 2
        });
    });

    it("Test: from Approve to Completed positive flow", async () => {
        await DeployOffer()
        let mint_amount = price
        await mint(deployer, master, jobOffer.address, mint_amount)
        // Approve
        let w = await platform.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeApprove({
                        $$type: "Approve",
                        amount: mint_amount,
                    })
                ).endCell()
            }
        )
        expect(w.transactions).toHaveTransaction({
            from:platform.address,
            to: jobOffer.address,
            success: true,
            op: 0x013f,
            outMessagesCount: 1 // notification 
        })
        // Total fees 3978328n
        let JOstateCheck = await jobOffer.getJobData()
        expect(JOstateCheck.state).toEqual(1n) // Offer published

        // Try get by poster
        let get_poster_job_res = await poster.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeGetJob({
                        $$type: "GetJob",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        expect(get_poster_job_res.transactions).toHaveTransaction({
            from: poster.address,
            to: jobOffer.address,
            success: false,
        });

        // Try get by doer
        let get_job_res = await doer.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeGetJob({
                        $$type: "GetJob",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        let getJobData = await jobOffer.getJobData()
        expect(getJobData.state).toBe(2n)
        expect(get_job_res.transactions).toHaveTransaction({
            from: doer.address,
            to: jobOffer.address,
            success: true,
        });

        // Get job again by third user
        let get_job_again = await third_user.send(
            {
                value: TransferAmount,
                to: jobOffer.address,
                body: beginCell().store(
                    storeGetJob({
                        $$type: "GetJob",
                        query_id: 1n
                    })
                ).endCell()
            }
        )
        expect(get_job_again.transactions).toHaveTransaction({
            from: third_user.address,
            to: jobOffer.address,
            success: false,
        });

        // Complete job by another users
        let complete_msg = {
            value: TransferAmount,
            to: jobOffer.address,
            body: beginCell().store(
                storeCompleteJob({
                    $$type: "CompleteJob",
                    query_id: 1n
                })
            ).endCell()
        }
        let completeByPlatform = await platform.send(
            complete_msg
        )
        expect(completeByPlatform.transactions).toHaveTransaction({from: platform.address, to: jobOffer.address, success: false})
        let JOStateData = await jobOffer.getJobData()
        expect(JOStateData.state).toBe(2n)
        // Complete by Doer
        let completeByDoer = await doer.send(
            complete_msg
        )
        JOStateData = await jobOffer.getJobData()
        expect(JOStateData.state).toBe(3n)
        expect(completeByDoer.transactions).toHaveTransaction({from: doer.address, to: jobOffer.address, success: true})
        
        // Confirm Job 
        let confirmJobMsg = {
            value: TransferAmount,
            to: jobOffer.address,
            body: beginCell().store(
                storeConfirmJob({
                    $$type: "ConfirmJob",
                    query_id: 1n
                })
            ).endCell()
        }
        // confirm by not owner
        let confirmByDoer = await doer.send(
            confirmJobMsg
        )
        expect(confirmByDoer.transactions).toHaveTransaction({from: doer.address, to: jobOffer.address, success: false})
        // confirm by owner 
        let confirmByOwner = await poster.send(
            confirmJobMsg
        )
        expect(confirmByOwner.transactions).toHaveTransaction({from: poster.address, to: jobOffer.address, success: true})
        let jobOfferJWData = await JOJW.getGetWalletData()
        expect(jobOfferJWData.balance).toBe(0n)

        // HERE IS PROBLEM. Jetton was sent to her znaet address. Need fix
        let tes = blockchain.openContract(TokenWallet.fromAddress(Address.parse("EQBTa4whhrgzTwcr344FHvCO3yUUyik9k6W1Z7qTD3J2N6Qh")))
    });





    it("Test: should witdraw", async () => {
        await DeployOffer()

        let mint_amount = price
        await mint(deployer, master, jobOffer.address, mint_amount)
        await poster.send(
            {
                value: toNano(2),
                to: jobOffer.address,
                body: beginCell().store(
                    storeWithdraw({
                        $$type: "Withdraw",
                        to: poster.address,
                        amount: mint_amount
                    })
                ).endCell()
            }
        )
        expect((await JOJW.getGetWalletData()).balance).toBeLessThanOrEqual(0n)
    });


    



    // it("Test: send transfers", async () => {
    // });

    // it("Test: Deploy offer", async () => {
    // });

    // it("Test: Revoke offer", async () => {
       
    // });
});
